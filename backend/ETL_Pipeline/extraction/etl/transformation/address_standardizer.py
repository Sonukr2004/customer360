"""
Address normalization: replaces abbreviated tokens ("St." -> "Street",
"Rd" -> "Road") using the lookup table in reference.reference_address.

Matches whole tokens only, so "Street" is never partially matched and
mangled just because "St" is a known abbreviation.
"""

import re

from etl.transformation.cleaner import trim


def load_reference_map(session):
    """
    Reads reference.reference_address and returns a dict keyed by lowercased
    short form (both with and without a trailing period, so "St." and "St"
    both resolve) -> long form.
    """
    from etl.transformation.models import ReferenceAddress

    mapping = {}
    for row in session.query(ReferenceAddress).all():
        key = row.short_form.strip().lower()
        mapping[key] = row.long_form
        mapping[key.rstrip(".")] = row.long_form
    return mapping


def standardize_address(address, ref_map):
    address = trim(address)
    if address is None:
        return None

    tokens = address.split(" ")
    standardized = []
    for token in tokens:
        lookup_key = re.sub(r"[.,]$", "", token).lower()
        if lookup_key in ref_map:
            standardized.append(ref_map[lookup_key])
        else:
            standardized.append(token.rstrip(","))
    return " ".join(standardized)
