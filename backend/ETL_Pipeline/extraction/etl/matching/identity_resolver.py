"""
Orchestrates identity resolution: fetches every staged record, runs the
matching rules in the PS's stated order (exact email -> exact phone ->
fuzzy name+address), and groups matched records into clusters -- each
cluster is one candidate Golden Customer, ready for survivorship.

Also derives, per source record, which rule was responsible for including
it in its cluster (for identity_map.match_type / match_score) -- a record
that matched by exact email keeps that as its strongest evidence even if
it's also loosely fuzzy-similar to something else in the same cluster.
"""

import logging

from sqlalchemy import text

from etl.matching.exact_match import match_by_email, match_by_phone
from etl.matching.fuzzy_match import match_by_name_address

logger = logging.getLogger(__name__)

# Priority order for reporting match_type when a record is linked into its
# cluster via more than one edge -- exact evidence always outranks fuzzy.
RULE_STRENGTH = {"exact_email": 3, "exact_phone": 2, "fuzzy_name_address": 1}


class UnionFind:
    """Standard union-find / disjoint-set with path compression."""

    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def groups(self):
        """Returns {root_index: [member_indices]}."""
        result = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            result.setdefault(root, []).append(i)
        return result


def fetch_staged_records(session, batch_id=None):
    """
    Reads every row from staging.staging_core_banking / _credit_card /
    _loan into a unified list of dicts. If batch_id is given, only that
    batch's rows are fetched (matching should run on one batch at a time,
    same as transformation).
    """
    records = []

    batch_filter = "WHERE batch_id = :batch_id" if batch_id else ""
    params = {"batch_id": batch_id} if batch_id else {}

    core_rows = session.execute(text(f"""
        SELECT source_customer_id, name, email, phone, dob, address
        FROM staging.staging_core_banking {batch_filter}
    """), params).fetchall()
    for row in core_rows:
        records.append({
            "source_system": "SourceA",
            "source_record_id": row.source_customer_id,
            "name": row.name, "email": row.email, "phone": row.phone,
            "dob": str(row.dob) if row.dob else None, "address": row.address,
        })

    card_rows = session.execute(text(f"""
        SELECT source_customer_id, name, email, phone, address, credit_limit
        FROM staging.staging_credit_card {batch_filter}
    """), params).fetchall()
    for row in card_rows:
        records.append({
            "source_system": "SourceB",
            "source_record_id": row.source_customer_id,
            "name": row.name, "email": row.email, "phone": row.phone,
            "dob": None, "address": row.address,
            "credit_limit": row.credit_limit,
        })

    loan_rows = session.execute(text(f"""
        SELECT source_customer_id, name, phone, address, loan_amount
        FROM staging.staging_loan {batch_filter}
    """), params).fetchall()
    for row in loan_rows:
        records.append({
            "source_system": "SourceC",
            "source_record_id": row.source_customer_id,
            "name": row.name, "email": None, "phone": row.phone,
            "dob": None, "address": row.address,
            "loan_amount": row.loan_amount,
        })

    logger.info("Fetched %d staged records for matching.", len(records))
    return records


def run_matching(records, threshold=0.85):
    """
    Runs all three matching rules in order. Returns (uf, edges) where edges
    is a list of (i, j, rule_name, score) -- exact-match edges get score 1.0.
    """
    uf = UnionFind(len(records))
    edges = []

    edges += [(a, b, rule, 1.0) for a, b, rule in match_by_email(records, uf)]
    edges += [(a, b, rule, 1.0) for a, b, rule in match_by_phone(records, uf)]
    edges += match_by_name_address(records, uf, threshold=threshold)

    return uf, edges


def _best_match_info(node_indices, edges):
    """
    For each node index in a cluster, finds the strongest edge touching it
    (exact_email > exact_phone > fuzzy_name_address) and returns
    {index: (match_type, match_score)}. A node with no edges (a singleton
    cluster) gets ("unmatched", None).
    """
    best = {}
    for a, b, rule, score in edges:
        for node in (a, b):
            if node not in node_indices:
                continue
            current = best.get(node)
            if current is None or RULE_STRENGTH[rule] > RULE_STRENGTH[current[0]]:
                best[node] = (rule, score)

    return {idx: best.get(idx, ("unmatched", None)) for idx in node_indices}


def build_clusters(records, uf, edges):
    """
    Returns a list of clusters, each:
        {
            "records": [record_dict, ...],
            "match_info": {source_record_id: (match_type, match_score)},
        }
    """
    groups = uf.groups()
    clusters = []

    for member_indices in groups.values():
        match_info_by_index = _best_match_info(set(member_indices), edges)
        cluster_records = [records[i] for i in member_indices]
        match_info = {
            records[i]["source_record_id"]: match_info_by_index[i] for i in member_indices
        }
        clusters.append({"records": cluster_records, "match_info": match_info})

    return clusters


def resolve_identities(session, batch_id=None, threshold=0.85):
    """Convenience entrypoint: fetch + match + cluster in one call."""
    records = fetch_staged_records(session, batch_id=batch_id)
    uf, edges = run_matching(records, threshold=threshold)
    clusters = build_clusters(records, uf, edges)
    logger.info(
        "Matching produced %d clusters from %d records (%d match edges).",
        len(clusters), len(records), len(edges),
    )
    return clusters
