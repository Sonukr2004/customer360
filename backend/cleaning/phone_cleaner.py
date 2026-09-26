"""
Cleans and standardizes customer phone number fields.
- Strips all non-digit characters
- Removes country code (+91) if present
- Validates final length is a 10-digit number
- Returns None for missing or invalid phone numbers
"""

import re

from cleaning.null_handler import normalize_nulls


def clean_phone(phone):
    """
    Cleans a raw phone number string. Returns None if missing or invalid.
    """
    phone = normalize_nulls(phone)
    if phone is None:
        return None

    digits = re.sub(r"\D", "", str(phone))  # strip non-digit characters

    # Strip Indian country code if present (91 + 10 digits = 12 digits)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if len(digits) != 10:
        return None

    return digits