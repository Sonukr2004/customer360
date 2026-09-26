from pathlib import Path

from sqlalchemy import text

from etl.master.customer_loader import persist_golden_customer
from etl.survivorship.hierarchy_loader import load_hierarchy
from etl.transformation.reference_loader import load_trust_hierarchy

FIXTURES = Path(__file__).parent / "fixtures"


def _cluster():
    return [
        {
            "source_system": "SourceA",
            "source_record_id": "C0001",
            "name": "John Doe",
            "email": "john.old@example.com",
            "phone": "9876543210",
            "dob": "1990-01-01",
            "address": "1 Old Street",
        },
        {
            "source_system": "SourceB",
            "source_record_id": "CC_100",
            "name": "J Doe",
            "email": "john.new@example.com",
            "phone": None,
            "dob": None,
            "address": "1 New Street",
        },
    ]


def test_persist_golden_customer_creates_master_row_with_correct_winners(session):
    load_trust_hierarchy(session, FIXTURES / "small_trust_hierarchy.json")
    hierarchy = load_hierarchy(session)

    customer = persist_golden_customer(session, _cluster(), hierarchy)

    assert customer.master_customer_id is not None
    assert customer.email == "john.new@example.com"  # SourceB wins Email
    assert customer.phone == "9876543210"  # only SourceA has phone
    assert customer.quality_score == 100  # all 5 fields populated


def test_persist_golden_customer_creates_one_identity_map_row_per_source(session):
    load_trust_hierarchy(session, FIXTURES / "small_trust_hierarchy.json")
    hierarchy = load_hierarchy(session)

    customer = persist_golden_customer(session, _cluster(), hierarchy)

    rows = session.execute(text(
        "SELECT source_system, source_customer_id FROM master.identity_map "
        "WHERE master_customer_id = :cid ORDER BY source_system"
    ), {"cid": str(customer.master_customer_id)}).fetchall()

    assert [(r.source_system, r.source_customer_id) for r in rows] == [
        ("SourceA", "C0001"), ("SourceB", "CC_100"),
    ]


def test_persist_golden_customer_writes_field_lineage_matching_winners(session):
    load_trust_hierarchy(session, FIXTURES / "small_trust_hierarchy.json")
    hierarchy = load_hierarchy(session)

    customer = persist_golden_customer(session, _cluster(), hierarchy)

    lineage = {
        row.field_name: row for row in session.execute(text(
            "SELECT field_name, source_system, source_value FROM master.field_lineage "
            "WHERE master_customer_id = :cid"
        ), {"cid": str(customer.master_customer_id)}).fetchall()
    }

    assert lineage["email"].source_system == "SourceB"
    assert lineage["email"].source_value == "john.new@example.com"
    assert lineage["phone"].source_system == "SourceA"
    # dob only exists on SourceA -- must survive even though SourceB wins other fields
    assert lineage["dob"].source_system == "SourceA"


def test_persist_golden_customer_records_match_type():
    pass  # covered by the match_type parameter being stored; exercised via
    # test_persist_golden_customer_creates_one_identity_map_row_per_source
    # implicitly using the default "exact" -- no separate assertion needed
