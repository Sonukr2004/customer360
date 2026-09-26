"""
Email normalization: trims whitespace and lowercases, e.g.
" JOHN@GMAIL.COM " -> "john@gmail.com".
"""

from etl.transformation.cleaner import trim


def standardize_email(email):
    email = trim(email)
    if email is None:
        return None
    return email.lower()
