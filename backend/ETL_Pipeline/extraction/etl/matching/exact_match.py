"""
Exact matching rules, per the PS's stated order:
    1. Exact match - Email
    2. Exact match - Phone

Both rules only link records from DIFFERENT source systems -- "match if
email matches BETWEEN 2 sources" is explicit in the PS about cross-source
comparison. Two rows from the same source sharing an email/phone is a
duplicate-ID data quality issue (already caught by
etl.transformation.duplicate_checker), not an identity match.
"""

from collections import defaultdict


def match_by_field(records, uf, field_name, rule_name):
    """
    Unions any two records (different source systems) that share the same
    non-null value for `field_name`. Returns the list of (i, j, rule_name)
    edges actually created.

    records: list of dicts with at least "source_system" and `field_name`.
    uf: a UnionFind instance (see identity_resolver.UnionFind), mutated in place.
    """
    by_value = defaultdict(list)
    for idx, rec in enumerate(records):
        value = rec.get(field_name)
        if value:
            by_value[value].append(idx)

    edges = []
    for indices in by_value.values():
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                a, b = indices[i], indices[j]
                if records[a]["source_system"] != records[b]["source_system"]:
                    uf.union(a, b)
                    edges.append((a, b, rule_name))
    return edges


def match_by_email(records, uf):
    return match_by_field(records, uf, "email", "exact_email")


def match_by_phone(records, uf):
    return match_by_field(records, uf, "phone", "exact_phone")
