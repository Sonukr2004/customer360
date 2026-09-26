"""
Integration test: runs the full extraction orchestration (validate -> batch
-> load) against small fixture files, then verifies the actual rows landed
in Postgres -- including that the Loan source loads correctly from JSONL,
not just CSV.
"""

from pathlib import Path

from sqlalchemy import text

from etl.ingestion.extract import run_extraction
from etl.ingestion.loader import load_core_banking, load_credit_card, load_loan, load_transactions

FIXTURES = Path(__file__).parent / "fixtures"

SMALL_SOURCES = [
    ("core_banking", FIXTURES / "small_core_banking.csv", load_core_banking),
    ("credit_card", FIXTURES / "small_credit_card.csv", load_credit_card),
    ("loan", FIXTURES / "small_loan.jsonl", load_loan),
    ("transaction", FIXTURES / "small_transactions.csv", load_transactions),
]


def test_full_extraction_run_lands_all_sources():
    summary = run_extraction(sources=SMALL_SOURCES)

    assert summary["status"] == "LOADED"
    assert summary["errors"] == {}
    assert summary["rows_loaded"] == {
        "core_banking": 2,
        "credit_card": 1,
        "loan": 1,
        "transaction": 2,
    }


def test_extraction_tags_every_row_with_the_same_batch_id(session):
    summary = run_extraction(sources=SMALL_SOURCES)
    batch_id = summary["batch_id"]

    for table in (
        "landing.landing_core_banking",
        "landing.landing_credit_card",
        "landing.landing_loan",
        "landing.landing_transaction",
    ):
        distinct_batches = session.execute(
            text(f"SELECT DISTINCT batch_id::text FROM {table}")
        ).scalars().all()
        assert distinct_batches == [batch_id], f"{table} has rows from an unexpected batch"


def test_loan_data_loads_correctly_from_jsonl_format(session):
    run_extraction(sources=SMALL_SOURCES)
    row = session.execute(
        text("SELECT loan_cust_id, name, phone, loan_amt FROM landing.landing_loan")
    ).fetchone()
    assert row.loan_cust_id == "L_500"
    assert row.name == "Jon Doe"
    assert row.phone == "9876543210"
    assert float(row.loan_amt) == 15000.0


def test_landing_data_is_raw_not_cleaned(session):
    """Landing must preserve values exactly as given (e.g. 'J. Doe', not
    Proper-Cased or deduplicated against 'John Doe') -- cleaning is a later
    stage, not part of extraction."""
    run_extraction(sources=SMALL_SOURCES)
    row = session.execute(
        text("SELECT name, address FROM landing.landing_credit_card WHERE cust_ref = 'CC_100'")
    ).fetchone()
    assert row.name == "J. Doe"
    assert row.address == "12 MG Blvd."  # NOT standardized to "12 MG Boulevard" yet


def test_batch_created_even_when_one_source_file_is_invalid():
    """If one file fails validation, the batch still loads everything that
    IS valid, and reports the failure -- it doesn't crash the whole run."""
    bad_sources = [
        ("core_banking", FIXTURES / "small_core_banking.csv", load_core_banking),
        ("credit_card", FIXTURES / "core_banking_missing_column.csv", load_credit_card),  # wrong columns
    ]
    summary = run_extraction(sources=bad_sources)

    assert summary["rows_loaded"] == {"core_banking": 2}
    assert "credit_card" in summary["errors"]
    assert summary["status"] == "PARTIALLY_LOADED"
