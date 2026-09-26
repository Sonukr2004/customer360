"""
Normalizes all 'missing value' representations to a single consistent form: None.
Run this BEFORE any other cleaner, so downstream functions can assume they're
getting either a real value or None — never "NaN", "null", empty string, etc.
"""

import math


def normalize_nulls(value):
    """
    Converts any null-like representation to Python None.
    Handles: None, NaN (float), and common string representations of missing data.
    """
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in ("", "nan", "null", "n/a", "na", "none"):
            return None

    return value