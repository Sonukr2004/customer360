"""
Standardizes address fields using a reference data lookup
(e.g., converts "St." -> "Street", "Rd" -> "Road").

Matches whole tokens only, so "Street" is never partially matched
and mangled by a substring replace.
"""

import csv
import re

from cleaning.null_handler import normalize_nulls


def load_reference_map(csv_path):
    """
    Loads the reference_data.csv file into a dict mapping
    lowercased short form -> long form (e.g., {"st": "Street", "rd": "Road"}).
    Expects a CSV with two columns: Short_Form, Long_Form (header optional).
    """
    mapping = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            short_form, long_form = row[0].strip(), row[1].strip()
            if short_form.lower() in ("short_form", "short form"):
                continue  # skip header row if present
            mapping[short_form.lower()] = long_form
    return mapping


def standardize_address(address, ref_map):
    """
    Standardizes an address string by replacing abbreviated tokens
    with their long form, using the provided reference map.
    Returns None if the address is missing.
    """
    address = normalize_nulls(address)
    if address is None:
        return None

    address = str(address).strip()
    tokens = address.split()

    standardized_tokens = []
    for token in tokens:
        # Strip trailing punctuation (e.g., "St." -> "St") for lookup purposes only
        lookup_key = re.sub(r"[.,]$", "", token).lower()
        if lookup_key in ref_map:
            standardized_tokens.append(ref_map[lookup_key])
        else:
            standardized_tokens.append(token)

    return " ".join(standardized_tokens)