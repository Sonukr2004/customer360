"""
Survivorship engine: given a cluster of source records (all representing
the SAME real customer, per whichever identity resolution produced the
grouping) and the trust hierarchy, picks the winning value for each field.

This is deliberately pure logic -- no DB access, no side effects -- so it's
trivial to unit test and doesn't care how the cluster was formed (fuzzy
matching, exact matching, or a hand-verified ground truth mapping for
testing). The one rule from the PS this must never violate: survivorship
is FIELD-SPECIFIC. There is no single "most trusted source" -- SourceA can
win Phone while SourceB wins Email, in the same cluster, if that's what the
hierarchy says.
"""

import logging

logger = logging.getLogger(__name__)

# Golden Record fields and the trust_hierarchy.json key each maps to.
FIELD_MAP = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "dob": "DOB",
    "address": "Address",
}


def resolve_field(field_name, candidates, field_hierarchy):
    """
    candidates: list of (source_system, value, source_record_id) tuples.
    field_hierarchy: {source_system: priority_rank} for this ONE field
        (i.e. hierarchy["Email"], not the whole hierarchy dict).

    Returns (value, source_system, source_record_id) for the winner, or
    (None, None, None) if every candidate is null.

    Candidates with a null value are never eligible to win, regardless of
    their source's priority -- a highly-trusted source that simply didn't
    provide this field must not blank out a value another source DID
    provide.

    If a source in the candidates has no entry in field_hierarchy (the
    config doesn't mention it for this field), it's treated as lowest
    priority rather than crashing -- but this is logged, since it usually
    means the hierarchy config is incomplete and should be reviewed.
    """
    non_null = [c for c in candidates if c[1] is not None]
    if not non_null:
        return None, None, None

    if not field_hierarchy:
        logger.warning(
            "No trust hierarchy entries for field '%s' -- defaulting to the "
            "first available source (%s). Trust_hierarchy config may be incomplete.",
            field_name, non_null[0][0],
        )
        source_system, value, source_record_id = non_null[0]
        return value, source_system, source_record_id

    def rank_of(candidate):
        source_system = candidate[0]
        if source_system not in field_hierarchy:
            logger.warning(
                "Source '%s' has no priority entry for field '%s' -- treating as lowest priority.",
                source_system, field_name,
            )
            return len(field_hierarchy) + 1
        return field_hierarchy[source_system]

    winner_source, winner_value, winner_source_record_id = min(non_null, key=rank_of)
    return winner_value, winner_source, winner_source_record_id


def build_golden_fields(cluster_records, hierarchy):
    """
    cluster_records: list of dicts, each with keys matching FIELD_MAP's
        left-hand side (name, email, phone, dob, address) plus
        "source_system" and "source_record_id".
    hierarchy: output of hierarchy_loader.load_hierarchy() -- the FULL
        {field_name: {source: rank}} dict, not one field's slice.

    Returns {internal_field_name: {"value", "source_system", "source_record_id"}}
    for every field in FIELD_MAP.
    """
    golden = {}
    for internal_name, hierarchy_key in FIELD_MAP.items():
        candidates = [
            (rec["source_system"], rec.get(internal_name), rec["source_record_id"])
            for rec in cluster_records
        ]
        value, source_system, source_record_id = resolve_field(
            hierarchy_key, candidates, hierarchy.get(hierarchy_key, {})
        )
        golden[internal_name] = {
            "value": value,
            "source_system": source_system,
            "source_record_id": source_record_id,
        }
    return golden


def quality_score(golden_fields):
    """Percentage of Golden Record fields that are non-null (0-100)."""
    populated = sum(1 for f in golden_fields.values() if f["value"] is not None)
    return round((populated / len(golden_fields)) * 100)
