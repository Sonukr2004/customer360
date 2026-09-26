"""
File validation for the extraction stage: checks a source file exists,
is non-empty, and (for CSVs) has the required columns before we attempt
to load a single row into `landing`.
"""

import csv
import json
from pathlib import Path

REQUIRED_COLUMNS = {
    "core_banking": ["Customer_ID", "Name", "Email", "Phone", "DOB", "Address"],
    "credit_card": ["Cust_Ref", "Name", "Email", "Phone", "Credit_Limit", "Address"],
    "loan": ["Loan_Cust_ID", "Name", "Phone", "Loan_Amt", "Address"],
    "transaction": ["Txn_ID", "Account_ID", "Amount", "Date", "Type"],
}


class FileValidationError(Exception):
    """Raised when a source file fails validation -- caught by the caller
    so one bad file doesn't crash the whole batch (graceful error handling,
    per the Software Engineering Excellence checklist)."""


def validate_exists_and_nonempty(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileValidationError(f"File not found: {file_path}")
    if path.stat().st_size == 0:
        raise FileValidationError(f"File is empty: {file_path}")
    return path


def validate_csv_columns(file_path, source_key):
    """Checks the CSV header contains every column required for `source_key`."""
    expected = REQUIRED_COLUMNS[source_key]
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
    missing = [c for c in expected if c not in header]
    if missing:
        raise FileValidationError(
            f"{file_path} is missing required column(s) for '{source_key}': {missing}"
        )
    return header


def validate_jsonl_columns(file_path, source_key):
    """Checks the first JSONL line contains every required key for `source_key`."""
    expected = REQUIRED_COLUMNS[source_key]
    with open(file_path, encoding="utf-8") as f:
        first_line = f.readline().strip()
    if not first_line:
        raise FileValidationError(f"{file_path} has no data rows")
    try:
        first_row = json.loads(first_line)
    except json.JSONDecodeError as e:
        raise FileValidationError(f"{file_path} is not valid JSONL: {e}")
    missing = [c for c in expected if c not in first_row]
    if missing:
        raise FileValidationError(
            f"{file_path} is missing required key(s) for '{source_key}': {missing}"
        )
    return list(first_row.keys())


def validate_source_file(file_path, source_key):
    """
    Runs the full validation chain for one source file:
    exists -> non-empty -> has required columns/keys.
    Dispatches to CSV or JSONL validation based on file extension.
    """
    path = validate_exists_and_nonempty(file_path)
    if path.suffix.lower() == ".jsonl":
        validate_jsonl_columns(path, source_key)
    else:
        validate_csv_columns(path, source_key)
    return True
