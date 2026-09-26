"""
Full end-to-end integration test: extraction -> transformation -> matching
-> survivorship -> persisted master.* rows, all against real Postgres,
using the small fixture data.

Fixture data: C0001 (John Doe)+CC_100+L_500 merge into one cluster;
C0002 (Jane Roe) is a singleton. See test_identity_resolver.py for the
matching-side breakdown of why.
"""

from pathlib import Path

from sqlalchemy import text

from etl.ingestion.extract import run_extraction
from etl.ingestion.loader import load_core_banking, load_credit_card, load_loan, load_transactions
from etl.master.customer_loader import persist_golden_customer
from etl.master.transaction_loader import link_transactions
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


def _run_full_pipeline(session):
    run_extraction(sources=SMALL_SOURCES)
    run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )
    hierarchy = load_hierarchy(session)
    clusters = resolve_identities(session, threshold=0.85)
    for cluster in clusters:
        persist_golden_customer(session, cluster["records"], hierarchy, match_info=cluster["match_info"])
    return clusters


def test_full_pipeline_persists_correct_number_of_golden_customers(session):
    clusters = _run_full_pipeline(session)
    assert len(clusters) == 2  # John Doe cluster + Jane Roe singleton

    count = session.execute(text("SELECT count(*) FROM master.master_customer")).scalar()
    assert count == 2


def test_full_pipeline_john_doe_cluster_has_correct_survivorship_winners(session):
    _run_full_pipeline(session)

    customer = session.execute(text(
        "SELECT mc.* FROM master.master_customer mc "
        "JOIN master.identity_map im ON im.master_customer_id = mc.master_customer_id "
        "WHERE im.source_system = 'SourceA' AND im.source_customer_id = 'C0001'"
    )).fetchone()

    # Phone hierarchy: SourceA > SourceB > SourceC. SourceA and SourceC agree
    # (9876543210); SourceB's conflicting 9999999999 must lose.
    assert customer.phone == "9876543210"
    # Address hierarchy: SourceB > SourceA > SourceC. SourceB's fixture value
    # ("12 MG Blvd." -- this fixture's reference map doesn't map "Blvd.",
    # unlike "St."/"Rd.", so it passes through unstandardized) genuinely
    # differs from A/C's standardized "12 MG Street".
    assert customer.address == "12 MG Blvd."


def test_full_pipeline_creates_three_identity_map_rows_for_john_doe(session):
    _run_full_pipeline(session)

    rows = session.execute(text("""
        SELECT im.source_system, im.source_customer_id FROM master.identity_map im
        WHERE im.master_customer_id = (
            SELECT master_customer_id FROM master.identity_map
            WHERE source_system = 'SourceA' AND source_customer_id = 'C0001'
        )
        ORDER BY im.source_system
    """)).fetchall()

    assert [(r.source_system, r.source_customer_id) for r in rows] == [
        ("SourceA", "C0001"), ("SourceB", "CC_100"), ("SourceC", "L_500"),
    ]


def test_full_pipeline_field_lineage_shows_correct_source_trace(session):
    _run_full_pipeline(session)

    lineage = session.execute(text("""
        SELECT field_name, source_system FROM master.field_lineage
        WHERE master_customer_id = (
            SELECT master_customer_id FROM master.identity_map
            WHERE source_system = 'SourceA' AND source_customer_id = 'C0001'
        )
    """)).fetchall()

    lineage_by_field = {row.field_name: row.source_system for row in lineage}
    assert lineage_by_field["phone"] == "SourceA"
    assert lineage_by_field["address"] == "SourceB"


def test_full_pipeline_jane_roe_singleton_persists_correctly(session):
    _run_full_pipeline(session)

    customer = session.execute(text(
        "SELECT mc.* FROM master.master_customer mc "
        "JOIN master.identity_map im ON im.master_customer_id = mc.master_customer_id "
        "WHERE im.source_system = 'SourceA' AND im.source_customer_id = 'C0002'"
    )).fetchone()

    assert customer.name == "Jane Roe"
    assert customer.email == "jane.roe@example.com"


def test_full_pipeline_creates_product_rows_for_each_source_record(session):
    _run_full_pipeline(session)

    core_count = session.execute(text("SELECT count(*) FROM master.core_product")).scalar()
    card_count = session.execute(text("SELECT count(*) FROM master.credit_card_product")).scalar()
    loan_count = session.execute(text("SELECT count(*) FROM master.loan_product")).scalar()

    # John Doe cluster: 1 core + 1 credit card + 1 loan; Jane Roe: 1 core
    assert core_count == 2
    assert card_count == 1
    assert loan_count == 1


def test_full_pipeline_links_transactions_to_correct_products(session):
    _run_full_pipeline(session)
    summary = link_transactions(session)

    # small_transactions.csv: T_001 -> C0001 (core), T_002 -> CC_100 (credit card)
    assert summary == {"linked": 2, "unresolved": 0}

    rows = session.execute(text(
        "SELECT txn_id, core_product_id, credit_card_product_id, loan_product_id "
        "FROM master.customer_transaction ORDER BY txn_id"
    )).fetchall()

    assert rows[0].txn_id == "T_001"
    assert rows[0].core_product_id is not None
    assert rows[0].credit_card_product_id is None
    assert rows[0].loan_product_id is None

    assert rows[1].txn_id == "T_002"
    assert rows[1].credit_card_product_id is not None
    assert rows[1].core_product_id is None


def test_full_pipeline_transaction_resolves_to_golden_customer_not_raw_id(session):
    """The specific PS scenario: Account_ID (a raw source ID) must resolve
    to the same Golden Customer regardless of which source it came from."""
    _run_full_pipeline(session)
    link_transactions(session)

    customer_ids = session.execute(text("""
        SELECT DISTINCT mc.master_customer_id
        FROM master.customer_transaction ct
        LEFT JOIN master.core_product cp ON cp.core_product_id = ct.core_product_id
        LEFT JOIN master.credit_card_product ccp ON ccp.credit_card_product_id = ct.credit_card_product_id
        JOIN master.master_customer mc ON mc.master_customer_id IN (cp.master_customer_id, ccp.master_customer_id)
    """)).fetchall()

    # T_001 (via C0001) and T_002 (via CC_100) belong to the SAME John Doe
    # cluster -- both transactions must resolve to the same Golden Customer.
    assert len(customer_ids) == 1
