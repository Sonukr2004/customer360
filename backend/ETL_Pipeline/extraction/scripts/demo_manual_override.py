#!/usr/bin/env python3
"""
Demonstrates a manual override against REAL data already in master.* --
picks one existing Golden Customer, changes their phone number, and shows
the before/after plus the resulting audit_log row.

Run this AFTER scripts/run_matching_and_survivorship.py has already
populated master.master_customer.

    python scripts/demo_manual_override.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text  # noqa: E402

from etl.ingestion.db import get_session  # noqa: E402
from etl.master.override_service import override_field  # noqa: E402


def main():
    session = get_session()

    try:
        customer = session.execute(text(
            "SELECT master_customer_id, name, phone FROM master.master_customer "
            "WHERE phone IS NOT NULL LIMIT 1"
        )).fetchone()

        if customer is None:
            print("No customers with a phone number found -- run the pipeline first.")
            return

        print(f"Before override:")
        print(f"  customer: {customer.name} ({customer.master_customer_id})")
        print(f"  phone:    {customer.phone}")

        new_phone = "9000000000"
        old_value, new_value = override_field(
            session, customer.master_customer_id, "phone", new_phone, changed_by="demo_script"
        )

        print(f"\nAfter override:")
        print(f"  phone: {new_value} (was {old_value})")

        audit_row = session.execute(text(
            "SELECT field_name, old_value, new_value, changed_by, action, changed_at "
            "FROM master.audit_log WHERE master_customer_id = :cid ORDER BY changed_at DESC LIMIT 1"
        ), {"cid": customer.master_customer_id}).fetchone()

        print(f"\naudit_log row created:")
        print(f"  field_name: {audit_row.field_name}")
        print(f"  old_value:  {audit_row.old_value}")
        print(f"  new_value:  {audit_row.new_value}")
        print(f"  changed_by: {audit_row.changed_by}")
        print(f"  action:     {audit_row.action}")
        print(f"  changed_at: {audit_row.changed_at}")

        lineage_row = session.execute(text(
            "SELECT source_system, source_value FROM master.field_lineage "
            "WHERE master_customer_id = :cid AND field_name = 'phone'"
        ), {"cid": customer.master_customer_id}).fetchone()

        print(f"\nfield_lineage updated:")
        print(f"  source_system: {lineage_row.source_system}")
        print(f"  source_value:  {lineage_row.source_value}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
