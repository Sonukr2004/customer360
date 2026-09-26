"""
Reads the trust hierarchy CONFIG back out of reference.trust_hierarchy
(loaded there by etl.transformation.reference_loader) into the shape the
survivorship engine actually needs: a per-field lookup of source -> rank.

This is deliberately DB-driven, not file-driven -- once trust_hierarchy.json
has been loaded into reference.trust_hierarchy, this is the single source
of truth survivorship reads from. If the hierarchy needs to change, you
update the table (or reload the file), not this code.
"""

from collections import defaultdict

from etl.transformation.models import TrustHierarchy


def load_hierarchy(session):
    """
    Returns {field_name: {source_system: priority_rank}}, e.g.:
        {"Email": {"SourceB": 1, "SourceA": 2, "SourceC": 3}, ...}

    priority_rank is an integer where 1 = highest priority (wins ties).
    """
    hierarchy = defaultdict(dict)
    for row in session.query(TrustHierarchy).all():
        hierarchy[row.field_name][row.source_system] = row.priority
    return dict(hierarchy)
