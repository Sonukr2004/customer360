from pathlib import Path

from etl.ingestion.loader import _blank_to_none, _parse_date, _parse_decimal, load_core_banking
from etl.ingestion.batch_manager import create_batch

FIXTURES = Path(__file__).parent / "fixtures"


def test_blank_to_none():
    assert _blank_to_none("") is None
    assert _blank_to_none("   ") is None
    assert _blank_to_none(None) is None
    assert _blank_to_none("John Doe") == "John Doe"


def test_parse_date_valid():
    d = _parse_date("1990-01-01", "row", "DOB")
    assert d.year == 1990 and d.month == 1 and d.day == 1


def test_parse_date_invalid_returns_none_not_raises():
    assert _parse_date("not-a-date", "row", "DOB") is None


def test_parse_date_blank_returns_none():
    assert _parse_date("", "row", "DOB") is None


def test_parse_decimal_valid():
    assert _parse_decimal("15,000.50", "row", "Amount") == 15000.50


def test_parse_decimal_invalid_returns_none_not_raises():
    assert _parse_decimal("not-a-number", "row", "Amount") is None


def test_load_core_banking_lands_rows_with_bad_dob_as_null(session):
    """core_banking_bad.csv has one row with DOB='not-a-date' -- that row
    must still land (with dob=NULL), not crash the whole file."""
    batch = create_batch(session, total_files=1)
    count = load_core_banking(session, batch, FIXTURES / "core_banking_bad.csv")
    assert count == 2

    from sqlalchemy import text
    rows = session.execute(
        text("SELECT customer_id, dob FROM landing.landing_core_banking ORDER BY customer_id")
    ).fetchall()
    assert rows[0].customer_id == "C0001"
    assert rows[0].dob is None  # unparseable DOB landed as NULL, row not dropped
    assert rows[1].customer_id == "C0002"
    assert rows[1].dob is not None
