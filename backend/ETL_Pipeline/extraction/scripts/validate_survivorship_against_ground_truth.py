"""
Validates the survivorship engine against REAL staged data, using
ground_truth_mapping.csv's verified customer groupings as a stand-in for
identity resolution (which hasn't been built yet). This proves
survivorship's logic is correct against real records before it's wired up
to whatever the matching stage eventually produces.

Not part of the production pipeline -- this is a diagnostic/validation
tool. Run from the project root:
    python scripts/validate_survivorship_against_ground_truth.py
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from etl.ingestion.db import get_session  # noqa: E402
from etl.survivorship.hierarchy_loader import load_hierarchy  # noqa: E402
from etl.survivorship.survivor_engine import build_golden_fields  # noqa: E402

GROUND_TRUTH_FILE = PROJECT_ROOT / "data" / "ground_truth_mapping.csv"


def _normalize_date(value):
    """
    ground_truth_mapping.csv stores dates as M/D/YYYY (e.g. "3/22/1959");
    staged data stores them as ISO YYYY-MM-DD (e.g. "1959-03-22"). Both
    represent the same date -- this normalizes either format to ISO so
    they can be compared on VALUE, not on string formatting.
    """
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return value  # unrecognized format -- leave as-is, comparison will just fail loudly


def fetch_staged_record(session, source_system, source_customer_id):
    """Pulls one staged record by source_system + source_customer_id,
    returning it in the dict shape survivor_engine expects."""
    table = {
        "SourceA": "staging_core_banking",
        "SourceB": "staging_credit_card",
        "SourceC": "staging_loan",
    }[source_system]

    from sqlalchemy import text
    row = session.execute(text(f"""
        SELECT name, {"email," if source_system != "SourceC" else ""} phone, address
               {", dob" if source_system == "SourceA" else ""}
        FROM staging.{table}
        WHERE source_customer_id = :sid
    """), {"sid": source_customer_id}).fetchone()

    if row is None:
        return None

    result = {
        "source_system": source_system,
        "source_record_id": source_customer_id,
        "name": row.name,
        "phone": row.phone,
        "address": row.address,
        "email": getattr(row, "email", None),
        "dob": str(getattr(row, "dob", None)) if getattr(row, "dob", None) else None,
    }
    return result


def main():
    session = get_session()
    hierarchy = load_hierarchy(session)

    with open(GROUND_TRUTH_FILE, newline="", encoding="utf-8") as f:
        ground_truth_rows = list(csv.DictReader(f))

    checked, name_matches, dob_matches, phone_matches = 0, 0, 0, 0

    for row in ground_truth_rows:
        cluster = []
        core_id = row.get("Core_Banking_Customer_ID", "").strip()
        if core_id:
            rec = fetch_staged_record(session, "SourceA", core_id)
            if rec:
                cluster.append(rec)

        cc_ref = row.get("Credit_Card_Cust_Ref", "").strip()
        if cc_ref:
            rec = fetch_staged_record(session, "SourceB", cc_ref)
            if rec:
                cluster.append(rec)

        loan_id = row.get("Loan_Cust_ID", "").strip()
        if loan_id:
            rec = fetch_staged_record(session, "SourceC", loan_id)
            if rec:
                cluster.append(rec)

        if not cluster:
            continue

        golden = build_golden_fields(cluster, hierarchy)
        checked += 1

        true_name = row.get("True_Name", "").strip()
        true_dob = row.get("True_DOB", "").strip()
        true_phone = row.get("True_Phone", "").strip()

        if true_name and golden["name"]["value"] == true_name:
            name_matches += 1
        if true_dob and golden["dob"]["value"] and _normalize_date(golden["dob"]["value"]) == _normalize_date(true_dob):
            dob_matches += 1
        if true_phone and golden["phone"]["value"] == true_phone:
            phone_matches += 1

    session.close()

    print(f"Ground truth rows checked: {checked}")
    print(f"  Name  matches survivorship winner: {name_matches}/{checked}")
    print(f"  DOB   matches survivorship winner: {dob_matches}/{checked}")
    print(f"  Phone matches survivorship winner: {phone_matches}/{checked}")


if __name__ == "__main__":
    main()
