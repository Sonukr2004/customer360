"""
Extraction / loading: reads each source file and inserts its rows into the
corresponding `landing` table, tagged with batch_id + source_file.

This is LANDING, not cleaning: values are stored as given (no trimming, no
Proper Case, no address standardization -- that's the next stage). The
only transformation here is casting raw strings into the column TYPES the
landing schema already declares (DATE, NUMERIC), since those columns are
typed, not TEXT. A row with an unparseable date/number is still landed
(with that one field NULL) rather than dropped or crashing the batch --
each such row is logged so nothing fails silently.
"""

import csv
import json
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from etl.ingestion.models import (
    LandingCoreBanking,
    LandingCreditCard,
    LandingLoan,
    LandingTransaction,
)

logger = logging.getLogger(__name__)


def _blank_to_none(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value != "" else None


def _parse_date(value, row_label, field_name):
    value = _blank_to_none(value)
    if value is None:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    logger.warning("%s: could not parse %s=%r as a date -- storing NULL", row_label, field_name, value)
    return None


def _parse_decimal(value, row_label, field_name):
    value = _blank_to_none(value)
    if value is None:
        return None
    try:
        return Decimal(value.replace(",", ""))
    except (InvalidOperation, AttributeError):
        logger.warning("%s: could not parse %s=%r as a number -- storing NULL", row_label, field_name, value)
        return None


def _read_csv_rows(file_path):
    with open(file_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_jsonl_rows(file_path):
    rows = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_core_banking(session, batch, file_path):
    """Source A. Loads core_banking.csv into landing.landing_core_banking."""
    rows = _read_csv_rows(file_path)
    source_file = Path(file_path).name

    mappings = []
    for i, row in enumerate(rows, start=1):
        label = f"{source_file} row {i} ({row.get('Customer_ID')})"
        mappings.append({
            "batch_id": batch.batch_id,
            "source_file": source_file,
            "customer_id": _blank_to_none(row.get("Customer_ID")),
            "name": _blank_to_none(row.get("Name")),
            "email": _blank_to_none(row.get("Email")),
            "phone": _blank_to_none(row.get("Phone")),
            "dob": _parse_date(row.get("DOB"), label, "DOB"),
            "address": _blank_to_none(row.get("Address")),
        })

    session.bulk_insert_mappings(LandingCoreBanking, mappings)
    session.commit()
    logger.info("Landed %d rows from %s -> landing.landing_core_banking", len(mappings), source_file)
    return len(mappings)


def load_credit_card(session, batch, file_path):
    """Source B. Loads credit_card.csv into landing.landing_credit_card."""
    rows = _read_csv_rows(file_path)
    source_file = Path(file_path).name

    mappings = []
    for i, row in enumerate(rows, start=1):
        label = f"{source_file} row {i} ({row.get('Cust_Ref')})"
        mappings.append({
            "batch_id": batch.batch_id,
            "source_file": source_file,
            "cust_ref": _blank_to_none(row.get("Cust_Ref")),
            "name": _blank_to_none(row.get("Name")),
            "email": _blank_to_none(row.get("Email")),
            "phone": _blank_to_none(row.get("Phone")),
            "credit_limit": _parse_decimal(row.get("Credit_Limit"), label, "Credit_Limit"),
            "address": _blank_to_none(row.get("Address")),
        })

    session.bulk_insert_mappings(LandingCreditCard, mappings)
    session.commit()
    logger.info("Landed %d rows from %s -> landing.landing_credit_card", len(mappings), source_file)
    return len(mappings)


def load_loan(session, batch, file_path):
    """
    Source C. Loads loan_system.csv OR loan_system.jsonl (whichever is
    passed) into landing.landing_loan -- both formats carry the same data.
    """
    path = Path(file_path)
    rows = _read_jsonl_rows(path) if path.suffix.lower() == ".jsonl" else _read_csv_rows(path)
    source_file = path.name

    mappings = []
    for i, row in enumerate(rows, start=1):
        label = f"{source_file} row {i} ({row.get('Loan_Cust_ID')})"
        mappings.append({
            "batch_id": batch.batch_id,
            "source_file": source_file,
            "loan_cust_id": _blank_to_none(row.get("Loan_Cust_ID")),
            "name": _blank_to_none(row.get("Name")),
            "phone": _blank_to_none(row.get("Phone")),
            "loan_amt": _parse_decimal(row.get("Loan_Amt"), label, "Loan_Amt"),
            "address": _blank_to_none(row.get("Address")),
        })

    session.bulk_insert_mappings(LandingLoan, mappings)
    session.commit()
    logger.info("Landed %d rows from %s -> landing.landing_loan", len(mappings), source_file)
    return len(mappings)


def load_transactions(session, batch, file_path):
    """Loads transaction_data.csv into landing.landing_transaction."""
    rows = _read_csv_rows(file_path)
    source_file = Path(file_path).name

    mappings = []
    for i, row in enumerate(rows, start=1):
        label = f"{source_file} row {i} ({row.get('Txn_ID')})"
        mappings.append({
            "batch_id": batch.batch_id,
            "source_file": source_file,
            "txn_id": _blank_to_none(row.get("Txn_ID")),
            "account_id": _blank_to_none(row.get("Account_ID")),
            "amount": _parse_decimal(row.get("Amount"), label, "Amount"),
            "transaction_date": _parse_date(row.get("Date"), label, "Date"),
            "transaction_type": _blank_to_none(row.get("Type")),
        })

    session.bulk_insert_mappings(LandingTransaction, mappings)
    session.commit()
    logger.info("Landed %d rows from %s -> landing.landing_transaction", len(mappings), source_file)
    return len(mappings)
