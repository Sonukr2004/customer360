from pathlib import Path

import pytest
from sqlalchemy import text

from etl.ingestion.extract import run_extraction
from etl.ingestion.loader import load_core_banking, load_credit_card, load_loan, load_transactions
from etl.master.customer_loader import persist_golden_customer
from etl.master.override_service import (
    CustomerNotFoundError,
    InvalidFieldError,
    override_field,
)
from etl.matching.identity_resolver import resolve_identities
from etl.survivorship.hierarchy_loader import load_hierarchy
from etl.transformation.transform import run_transformation

FIXTURES = Path(__file__).parent / "fixtures"

SMALL_SOURCES = [
    ("core_banking", FIXTURES / "small_core_banking.csv", load_core_banking),
    ("credit_card", FIXTURES / "small_credit_card.csv", load_credit_card),
    ("loan", FIXTURES / "small_loan.jsonl", load_loan),
    ("transaction", FIXTURES / "small_transactions.csv", load_transactions),
]


def _seed_one_customer(session):
    run_extraction(sources=SMALL_SOURCES)
    run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )
    hierarchy = load_hierarchy(session)
    clusters = resolve_identities(session, threshold=0.85)
    customer = None
    for cluster in clusters:
        c = persist_golden_customer(session, cluster["records"], hierarchy, match_info=cluster["match_info"])
        if len(cluster["records"]) == 3:  # the John Doe cluster
            customer = c
    return customer


def test_override_field_updates_master_customer(session):
    customer = _seed_one_customer(session)

    old_value, new_value = override_field(
        session, customer.master_customer_id, "phone", "9000000000", changed_by="test_steward"
    )

    assert old_value == "9876543210"  # SourceA's phone, per survivorship
    assert new_value == "9000000000"

    refetched = session.execute(text(
        "SELECT phone FROM master.master_customer WHERE master_customer_id = :cid"
    ), {"cid": customer.master_customer_id}).fetchone()
    assert refetched.phone == "9000000000"


def test_override_field_writes_audit_log_entry(session):
    customer = _seed_one_customer(session)
    override_field(session, customer.master_customer_id, "phone", "9000000000", changed_by="test_steward")

    row = session.execute(text(
        "SELECT field_name, old_value, new_value, changed_by, action FROM master.audit_log "
        "WHERE master_customer_id = :cid"
    ), {"cid": customer.master_customer_id}).fetchone()

    assert row.field_name == "phone"
    assert row.old_value == "9876543210"
    assert row.new_value == "9000000000"
    assert row.changed_by == "test_steward"
    assert row.action == "UPDATE"


def test_override_field_updates_field_lineage_to_datasteward(session):
    customer = _seed_one_customer(session)
    override_field(session, customer.master_customer_id, "phone", "9000000000")

    row = session.execute(text(
        "SELECT source_system, source_customer_id, source_value FROM master.field_lineage "
        "WHERE master_customer_id = :cid AND field_name = 'phone'"
    ), {"cid": customer.master_customer_id}).fetchone()

    assert row.source_system == "DataSteward"
    assert row.source_customer_id is None
    assert row.source_value == "9000000000"


def test_override_field_rejects_unknown_field(session):
    customer = _seed_one_customer(session)
    with pytest.raises(InvalidFieldError):
        override_field(session, customer.master_customer_id, "ssn", "123-45-6789")


def test_override_field_raises_for_unknown_customer(session):
    with pytest.raises(CustomerNotFoundError):
        override_field(session, "00000000-0000-0000-0000-000000000000", "phone", "9000000000")


def test_multiple_overrides_each_get_their_own_audit_row(session):
    customer = _seed_one_customer(session)
    override_field(session, customer.master_customer_id, "phone", "9000000000")
    override_field(session, customer.master_customer_id, "phone", "9111111111")

    count = session.execute(text(
        "SELECT count(*) FROM master.audit_log WHERE master_customer_id = :cid"
    ), {"cid": customer.master_customer_id}).scalar()
    assert count == 2

    final_phone = session.execute(text(
        "SELECT phone FROM master.master_customer WHERE master_customer_id = :cid"
    ), {"cid": customer.master_customer_id}).fetchone()
    assert final_phone.phone == "9111111111"
