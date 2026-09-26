"""
Cleans and standardizes customer name fields.
- Trims whitespace
- Collapses multiple spaces into one
- Converts to Proper Case (e.g., "JOHN doe" -> "John Doe")
"""

import re

from cleaning.null_handler import normalize_nulls


def clean_name(name):
    """
    Cleans a raw name string. Returns None if the input is missing/null-like.
    """
    name = normalize_nulls(name)
    if name is None:
        return None

    name = str(name).strip()
    name = re.sub(r"\s+", " ", name)  # collapse multiple spaces
    name = name.title()  # Proper Case

    return name if name else None