"""
Evaluates MATCHING accuracy (not survivorship) against
ground_truth_mapping.csv: for each ground-truth customer with more than
one known source ID, checks whether identity_map actually placed all of
those IDs under the same master_customer_id.

Run AFTER scripts/run_matching_and_survivorship.py, from the project root:
    python scripts/evaluate_matching_against_ground_truth.py
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text  # noqa: E402

from etl.ingestion.db import get_session  # noqa: E402

GROUND_TRUTH_FILE = PROJECT_ROOT / "data" / "ground_truth_mapping.csv"


def get_master_customer_id(session, source_system, source_customer_id):
    if not source_customer_id:
        return None
    row = session.execute(text("""
        SELECT master_customer_id FROM master.identity_map
        WHERE source_system = :src AND source_customer_id = :sid
    """), {"src": source_system, "sid": source_customer_id}).fetchone()
    return str(row.master_customer_id) if row else None


def main():
    session = get_session()
    correct, partial, wrong, total = 0, 0, 0, 0

    with open(GROUND_TRUTH_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        total += 1
        expected_ids = []

        core_id = row.get("Core_Banking_Customer_ID", "").strip()
        if core_id:
            expected_ids.append(("SourceA", core_id))

        dup_id = row.get("Core_Banking_Duplicate_IDs", "").strip()
        if dup_id:
            expected_ids.append(("SourceA", dup_id))

        cc_ref = row.get("Credit_Card_Cust_Ref", "").strip()
        if cc_ref:
            expected_ids.append(("SourceB", cc_ref))

        loan_id = row.get("Loan_Cust_ID", "").strip()
        if loan_id:
            expected_ids.append(("SourceC", loan_id))

        if len(expected_ids) <= 1:
            continue  # nothing to merge -- not a useful data point

        found_master_ids = {get_master_customer_id(session, src, sid) for src, sid in expected_ids}
        found_master_ids.discard(None)

        if len(found_master_ids) == 1:
            correct += 1
        elif len(found_master_ids) == len(expected_ids):
            wrong += 1
        else:
            partial += 1

    session.close()

    evaluable = correct + partial + wrong
    print(f"Ground truth rows: {total}")
    print(f"Rows with >1 expected source ID (evaluable): {evaluable}")
    print(f"  Fully merged correctly : {correct}")
    print(f"  Partially merged       : {partial}")
    print(f"  Not merged at all      : {wrong}")
    if evaluable:
        print(f"  Accuracy               : {correct / evaluable * 100:.1f}%")


if __name__ == "__main__":
    main()
