"""
Cleans and validates customer email fields.
- Trims whitespace, lowercases
- Validates basic email format
- Returns None for missing or malformed emails
"""

import re

from cleaning.null_handler import normalize_nulls

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_email(email):
    """
    Cleans a raw email string. Returns None if missing or invalid format.
    """
    email = normalize_nulls(email)
    if email is None:
        return None

    email = str(email).strip().lower()

    if not EMAIL_PATTERN.match(email):
        return None

    return email