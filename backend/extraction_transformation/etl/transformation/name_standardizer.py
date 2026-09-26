"""
Name normalization: trims whitespace, collapses internal spaces, and
converts to Proper Case, e.g. "JOHN DOE" / "john doe" -> "John Doe".
"""

from etl.transformation.cleaner import trim


def standardize_name(name):
    name = trim(name)
    if name is None:
        return None
    return name.title()
