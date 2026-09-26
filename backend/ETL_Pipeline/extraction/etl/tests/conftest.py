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
def _clean_tables():
    """Truncates landing, staging, and reference tables before every test,
    so tests never see rows left over from a previous test or a real run."""
    s = get_session()
    s.execute(text("""
        TRUNCATE TABLE
            master.audit_log,
            master.field_lineage,
            master.customer_transaction,
            master.loan_product,
            master.credit_card_product,
            master.core_product,
            master.identity_map,
            master.master_customer,
            staging.staging_transaction,
            staging.staging_loan,
            staging.staging_credit_card,
            staging.staging_core_banking,
            landing.landing_transaction,
            landing.landing_loan,
            landing.landing_credit_card,
            landing.landing_core_banking,
            landing.landing_batch,
            reference.reference_address,
            reference.trust_hierarchy
        RESTART IDENTITY CASCADE
    """))
    s.commit()
    s.close()
    yield
