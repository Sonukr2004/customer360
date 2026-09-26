"""
Orchestrates the transformation stage:

    reference_data.csv / trust_hierarchy.json  -> reference.*  (config, upserted)
    landing.landing_*                          -> staging.*    (cleaned + standardized)

Landing is append-only (each extraction run adds a new landing_batch and
new rows, on top of whatever was already there) -- so transformation must
only process the MOST RECENT batch, not landing's entire history, or
re-running extraction multiple times (e.g. while debugging a connection
issue) silently multiplies every row in staging by however many times
extraction was run. Staging itself is still a fully-derived layer for
that one batch: each run TRUNCATEs the staging tables and rebuilds them
from the latest batch in landing.

Run directly:
    python -m etl.transformation.transform
or via scripts/run_transformation.py from the project root.
"""

import logging

from sqlalchemy import text

from etl.ingestion import config
from etl.ingestion.db import get_session
from etl.ingestion.models import LandingBatch, LandingCoreBanking, LandingCreditCard, LandingLoan, LandingTransaction
from etl.transformation.address_standardizer import load_reference_map, standardize_address
from etl.transformation.duplicate_checker import find_duplicate_ids
from etl.transformation.email_standardizer import standardize_email
from etl.transformation.models import StagingCoreBanking, StagingCreditCard, StagingLoan, StagingTransaction
from etl.transformation.name_standardizer import standardize_name
from etl.transformation.phone_standardizer import standardize_phone
from etl.transformation.reference_loader import load_reference_address, load_trust_hierarchy

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_latest_batch_id(session):
    """
    Returns the batch_id of the most recently created landing_batch row,
    or None if landing_batch is empty (nothing has been extracted yet).
    """
    latest = session.query(LandingBatch).order_by(LandingBatch.uploaded_at.desc()).first()
    return latest.batch_id if latest else None


def _check_all_duplicates(session, batch_id):
    """
    Runs the duplicate-ID check across all four landing tables, SCOPED TO
    THE GIVEN BATCH ONLY, and returns {source: {duplicate_id: count}}.
    Never raises and never blocks the pipeline -- duplicates are surfaced
    for a data steward to review, not auto-resolved here.
    """
    return {
        "core_banking": find_duplicate_ids(session, LandingCoreBanking, "customer_id", "core_banking", batch_id=batch_id),
        "credit_card": find_duplicate_ids(session, LandingCreditCard, "cust_ref", "credit_card", batch_id=batch_id),
        "loan": find_duplicate_ids(session, LandingLoan, "loan_cust_id", "loan", batch_id=batch_id),
        "transaction": find_duplicate_ids(session, LandingTransaction, "txn_id", "transaction", batch_id=batch_id),
    }


def _truncate_staging(session):
    session.execute(text("""
        TRUNCATE TABLE
            staging.staging_transaction,
            staging.staging_loan,
            staging.staging_credit_card,
            staging.staging_core_banking
        RESTART IDENTITY
    """))
    session.commit()


def transform_core_banking(session, ref_map, batch_id):
    rows = session.query(LandingCoreBanking).filter(LandingCoreBanking.batch_id == batch_id).all()
    mappings = []
    for row in rows:
        mappings.append({
            "batch_id": row.batch_id,
            "source_file": row.source_file,
            "source_customer_id": row.customer_id,
            "name": standardize_name(row.name),
            "email": standardize_email(row.email),
            "phone": standardize_phone(row.phone),
            "dob": row.dob,  # already a DATE from landing; no further transform needed
            "address": standardize_address(row.address, ref_map),
        })
    session.bulk_insert_mappings(StagingCoreBanking, mappings)
    session.commit()
    logger.info("Staged %d rows -> staging.staging_core_banking", len(mappings))
    return len(mappings)


def transform_credit_card(session, ref_map, batch_id):
    rows = session.query(LandingCreditCard).filter(LandingCreditCard.batch_id == batch_id).all()
    mappings = []
    for row in rows:
        mappings.append({
            "batch_id": row.batch_id,
            "source_file": row.source_file,
            "source_customer_id": row.cust_ref,
            "name": standardize_name(row.name),
            "email": standardize_email(row.email),
            "phone": standardize_phone(row.phone),
            "credit_limit": row.credit_limit,
            "address": standardize_address(row.address, ref_map),
        })
    session.bulk_insert_mappings(StagingCreditCard, mappings)
    session.commit()
    logger.info("Staged %d rows -> staging.staging_credit_card", len(mappings))
    return len(mappings)


def transform_loan(session, ref_map, batch_id):
    rows = session.query(LandingLoan).filter(LandingLoan.batch_id == batch_id).all()
    mappings = []
    for row in rows:
        mappings.append({
            "batch_id": row.batch_id,
            "source_file": row.source_file,
            "source_customer_id": row.loan_cust_id,
            "name": standardize_name(row.name),
            "phone": standardize_phone(row.phone),
            "loan_amount": row.loan_amt,
            "address": standardize_address(row.address, ref_map),
        })
    session.bulk_insert_mappings(StagingLoan, mappings)
    session.commit()
    logger.info("Staged %d rows -> staging.staging_loan", len(mappings))
    return len(mappings)


def transform_transactions(session, batch_id):
    """Transactions have no name/email/phone/address to standardize -- they
    pass through as-is, already correctly typed from landing."""
    rows = session.query(LandingTransaction).filter(LandingTransaction.batch_id == batch_id).all()
    mappings = []
    for row in rows:
        mappings.append({
            "batch_id": row.batch_id,
            "source_file": row.source_file,
            "txn_id": row.txn_id,
            "account_id": row.account_id,
            "amount": row.amount,
            "transaction_date": row.transaction_date,
            "transaction_type": row.transaction_type,
        })
    session.bulk_insert_mappings(StagingTransaction, mappings)
    session.commit()
    logger.info("Staged %d rows -> staging.staging_transaction", len(mappings))
    return len(mappings)


def run_transformation(session=None, reference_file=None, hierarchy_file=None, batch_id=None):
    """
    Runs the full transformation stage, scoped to ONE batch (the most
    recent one in landing.landing_batch, unless batch_id is given
    explicitly -- tests pass an explicit batch_id from a fixture run).
    """
    owns_session = session is None
    if owns_session:
        session = get_session()

    reference_file = reference_file or config.REFERENCE_ADDRESS_FILE
    hierarchy_file = hierarchy_file or config.TRUST_HIERARCHY_FILE

    try:
        load_reference_address(session, reference_file)
        load_trust_hierarchy(session, hierarchy_file)

        ref_map = load_reference_map(session)

        target_batch_id = batch_id or get_latest_batch_id(session)
        if target_batch_id is None:
            raise RuntimeError(
                "No batches found in landing.landing_batch -- run extraction first."
            )

        duplicates = _check_all_duplicates(session, target_batch_id)

        _truncate_staging(session)

        counts = {
            "core_banking": transform_core_banking(session, ref_map, target_batch_id),
            "credit_card": transform_credit_card(session, ref_map, target_batch_id),
            "loan": transform_loan(session, ref_map, target_batch_id),
            "transaction": transform_transactions(session, target_batch_id),
        }
        counts["batch_id"] = str(target_batch_id)
        counts["duplicates_found"] = duplicates
        return counts
    finally:
        if owns_session:
            session.close()


if __name__ == "__main__":
    summary = run_transformation()
    duplicates = summary.pop("duplicates_found")
    batch_id = summary.pop("batch_id")

    print(f"\nTransformation complete (batch {batch_id}):")
    for source, count in summary.items():
        print(f"  {source}: {count}")

    any_duplicates = any(duplicates.values())
    if any_duplicates:
        print("\nDuplicate IDs detected within this batch (needs review):")
        for source, dupes in duplicates.items():
            for dup_id, occurrences in dupes.items():
                print(f"  {source}: {dup_id!r} appears {occurrences} times")
    else:
        print("\nNo duplicate IDs detected within this batch.")
