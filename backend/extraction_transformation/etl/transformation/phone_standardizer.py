"""
Phone normalization: strips all non-digit formatting characters (spaces,
dashes, parentheses, a leading '+'), e.g. "+91 98765-43210" -> "919876543210".

Deliberately does NOT add or strip a country code -- it keeps exactly the
digits the source provided, just without punctuation/whitespace, so a
plain 10-digit number stays 10 digits and a number given with a country
code keeps it.
"""

import re

from etl.transformation.cleaner import blank_to_none


def standardize_phone(phone):
    phone = blank_to_none(phone)
    if phone is None:
        return None
    digits = re.sub(r"\D", "", phone)
    return digits or None
