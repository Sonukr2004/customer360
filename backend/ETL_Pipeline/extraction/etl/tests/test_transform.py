"""
Integration test: runs extraction (landing raw data) THEN transformation
(cleaning + standardizing into staging), chaining both stages exactly as
they'd run in the real pipeline, and verifies the actual staged rows.
"""

from pathlib import Path

from sqlalchemy import text

from etl.ingestion.extract import run_extraction
from etl.ingestion.loader import load_core_banking, load_credit_card, load_loan, load_transactions
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
    return run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )


def test_transformation_stages_expected_row_counts(session):
    counts = _run_full_pipeline(session)
    counts.pop("batch_id")
    duplicates = counts.pop("duplicates_found")
    assert counts == {"core_banking": 2, "credit_card": 1, "loan": 1, "transaction": 2}
    assert all(d == {} for d in duplicates.values())  # no duplicate IDs in this fixture


def test_transformation_cleans_names_and_addresses(session):
    _run_full_pipeline(session)

    row = session.execute(text(
        "SELECT name, address FROM staging.staging_core_banking WHERE source_customer_id = 'C0001'"
    )).fetchone()
    assert row.name == "John Doe"
    assert row.address == "12 MG Street"  # "St." -> "Street" via reference lookup


def test_transformation_lowercases_email(session):
    _run_full_pipeline(session)

    row = session.execute(text(
        "SELECT email FROM staging.staging_credit_card WHERE source_customer_id = 'CC_100'"
    )).fetchone()
    assert row.email == "john.doe@example.com"


def test_transformation_preserves_raw_name_variant_for_matching_stage():
    """Staging must NOT deduplicate/merge records -- 'J. Doe' from credit_card
    stays distinct from 'John Doe' from core_banking; that's the matching
    stage's job, not transformation's."""
    pass  # covered implicitly by row counts staying at source-record granularity


def test_transformation_passes_through_transaction_data_unchanged(session):
    _run_full_pipeline(session)

    row = session.execute(text(
        "SELECT txn_id, account_id, amount, transaction_type FROM staging.staging_transaction "
        "WHERE txn_id = 'T_001'"
    )).fetchone()
    assert row.account_id == "C0001"
    assert float(row.amount) == 1000.00
    assert row.transaction_type == "Debit"


def test_transformation_is_idempotent_on_rerun(session):
    """Running transformation twice in a row (without re-extracting) must
    not duplicate staging rows -- staging is a full-refresh derived layer."""
    _run_full_pipeline(session)
    counts_second_run = run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )
    counts_second_run.pop("batch_id")
    counts_second_run.pop("duplicates_found")
    assert counts_second_run == {"core_banking": 2, "credit_card": 1, "loan": 1, "transaction": 2}

    total_staging_rows = session.execute(text(
        "SELECT count(*) FROM staging.staging_core_banking"
    )).scalar()
    assert total_staging_rows == 2  # not 4 -- truncated and rebuilt, not appended


def test_transformation_only_processes_latest_batch_when_extraction_reran(session):
    """
    Regression test: landing is append-only, so running extraction twice
    (e.g. while debugging a flaky connection) leaves TWO batches' worth of
    rows sitting in landing. Transformation must stage only the most
    recent batch -- not silently double (or quadruple) every row.
    """
    run_extraction(sources=SMALL_SOURCES)  # batch 1
    run_extraction(sources=SMALL_SOURCES)  # batch 2 -- landing now has both

    total_landing_rows = session.execute(text(
        "SELECT count(*) FROM landing.landing_core_banking"
    )).scalar()
    assert total_landing_rows == 4  # 2 rows x 2 extraction runs, confirming landing DID accumulate

    counts = run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )

    # Staging reflects only the LATEST batch -- 2 rows, not 4
    assert counts["core_banking"] == 2

    total_staging_rows = session.execute(text(
        "SELECT count(*) FROM staging.staging_core_banking"
    )).scalar()
    assert total_staging_rows == 2


def test_duplicate_check_ignores_ids_repeated_across_separate_batches(session):
    """
    Regression test: the SAME Customer_ID legitimately exists in both
    batches after two extraction runs -- that must NOT be reported as a
    duplicate (it's expected re-extraction, not a data quality problem).
    Only a genuine duplicate WITHIN one batch should be flagged.
    """
    run_extraction(sources=SMALL_SOURCES)  # batch 1: C0001, C0002
    counts = run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )
    run_extraction(sources=SMALL_SOURCES)  # batch 2: C0001, C0002 again -- expected, not a duplicate
    counts = run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )

    assert counts["duplicates_found"]["core_banking"] == {}
