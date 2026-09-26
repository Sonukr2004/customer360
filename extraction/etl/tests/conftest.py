"""
Test fixtures. Tests run against a REAL Postgres database (schema-qualified
tables, UUID PKs, and server-side defaults don't behave the same on SQLite),
so this points at TEST_DATABASE_URL (defaulting to a local Postgres
instance) and truncates the landing tables between tests.
"""

import os

import pytest
from sqlalchemy import text

os.environ.setdefault(
    "SUPABASE_DB_URL",
    os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/unibank_pytest"),
)

from etl.ingestion.db import get_session  # noqa: E402


@pytest.fixture()
def session():
    s = get_session()
    yield s
    s.close()


@pytest.fixture(autouse=True)
def _clean_landing_tables():
    """Truncates all landing tables (and cascades to nothing else, since
    landing has no children) before every test, so tests never see rows
    left over from a previous test or from a real extraction run."""
    s = get_session()
    s.execute(text("""
        TRUNCATE TABLE
            landing.landing_transaction,
            landing.landing_loan,
            landing.landing_credit_card,
            landing.landing_core_banking,
            landing.landing_batch
        RESTART IDENTITY CASCADE
    """))
    s.commit()
    s.close()
    yield
