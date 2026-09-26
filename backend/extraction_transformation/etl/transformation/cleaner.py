"""
Shared cleaning helpers used by every standardizer: null handling and
whitespace trimming. NULL means "the source didn't provide this value" --
we never turn a missing value into a placeholder string like "N/A" or
"Unknown".
"""


def blank_to_none(value):
    """Converts None, empty string, or whitespace-only string to None.
    Leaves any other value untouched (as a trimmed string)."""
    if value is None:
        return None
    text = str(value).strip()
    return text if text != "" else None


def trim(value):
    """Trims whitespace and collapses internal multi-space runs to one space."""
    value = blank_to_none(value)
    if value is None:
        return None
    return " ".join(value.split())
