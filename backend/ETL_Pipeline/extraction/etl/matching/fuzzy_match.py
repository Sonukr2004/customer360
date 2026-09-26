"""
Fuzzy matching rule (rule 3 in the PS's order): Name + Address, applied
only where email/phone didn't already establish a match. Blocked by
(first letter of name, first letter of address) to keep the comparison
tractable on the full ~3,100-record dataset -- a full O(n^2) comparison
without blocking is unnecessary and slow.

Unlike the exact rules, fuzzy matching is allowed WITHIN the same source
system too -- real source data can contain its own internal duplicates
(confirmed in ground_truth_mapping.csv's Core_Banking_Duplicate_IDs
column), and fuzzy name+address is the only rule that can catch those.
"""

from collections import defaultdict

from rapidfuzz import fuzz


def _block_key(record):
    name = (record.get("name") or "").strip().lower()
    address = (record.get("address") or "").strip().lower()
    return (name[:1], address[:1])


def match_by_name_address(records, uf, threshold=0.85):
    """
    Fuzzy-matches Name + Address for pairs sharing a block key that aren't
    already linked by an earlier (exact) rule. Both name and address must
    independently score >= threshold (0-1 scale) for the pair to union.

    Returns the list of (i, j, rule_name, score) edges created, where
    score is the average of the name and address similarity (0-1 scale).
    """
    blocks = defaultdict(list)
    for idx, rec in enumerate(records):
        blocks[_block_key(rec)].append(idx)

    threshold_pct = threshold * 100
    edges = []

    for indices in blocks.values():
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                a, b = indices[i], indices[j]
                if uf.find(a) == uf.find(b):
                    continue  # already matched by an earlier rule

                rec_a, rec_b = records[a], records[b]
                name_a, name_b = rec_a.get("name") or "", rec_b.get("name") or ""
                addr_a, addr_b = rec_a.get("address") or "", rec_b.get("address") or ""
                if not name_a or not name_b or not addr_a or not addr_b:
                    continue

                name_score = fuzz.token_sort_ratio(name_a, name_b)
                addr_score = fuzz.token_sort_ratio(addr_a, addr_b)

                if name_score >= threshold_pct and addr_score >= threshold_pct:
                    uf.union(a, b)
                    combined = round((name_score + addr_score) / 200, 4)  # -> 0-1 scale
                    edges.append((a, b, "fuzzy_name_address", combined))

    return edges
