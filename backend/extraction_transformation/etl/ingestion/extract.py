"""
Orchestrates ONE extraction run:

    validate all source files -> create a batch -> load each file into its
    landing table -> mark the batch LOADED (or FAILED)

Run directly:
    python -m etl.ingestion.extract
or via scripts/run_extraction.py from the project root.
"""

import logging

from etl.ingestion import config
from etl.ingestion.batch_manager import create_batch, mark_batch_status
from etl.ingestion.db import get_session
from etl.ingestion.file_validator import FileValidationError, validate_source_file
from etl.ingestion.loader import load_core_banking, load_credit_card, load_loan, load_transactions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# (source_key, file_path, loader_function) -- order matches the PS's file list
SOURCES = [
    ("core_banking", config.CORE_BANKING_FILE, load_core_banking),
    ("credit_card", config.CREDIT_CARD_FILE, load_credit_card),
    ("loan", config.LOAN_FILE, load_loan),
    ("transaction", config.TRANSACTION_FILE, load_transactions),
]


def run_extraction(sources=None):
    """
    Runs the full extraction stage. `sources` optionally overrides the
    default (source_key, file_path, loader_fn) list -- tests pass fixture
    paths here instead of the real dataset.

    Returns a summary dict; never raises for a single bad file -- each
    source is validated and loaded independently so one problem file
    doesn't block the others (graceful error handling).
    """
    sources = sources or SOURCES
    session = get_session()

    results = {}
    errors = {}

    # Validate everything up front so we know total_files/status before
    # creating the batch record.
    valid_sources = []
    for source_key, file_path, loader_fn in sources:
        try:
            validate_source_file(file_path, source_key)
            valid_sources.append((source_key, file_path, loader_fn))
        except FileValidationError as e:
            logger.error("Validation failed for '%s': %s", source_key, e)
            errors[source_key] = str(e)

    batch = create_batch(session, total_files=len(sources))

    try:
        for source_key, file_path, loader_fn in valid_sources:
            try:
                count = loader_fn(session, batch, file_path)
                results[source_key] = count
            except Exception as e:  # noqa: BLE001 -- one bad file must not sink the batch
                session.rollback()
                logger.exception("Failed to load '%s' (%s)", source_key, file_path)
                errors[source_key] = str(e)

        status = "LOADED" if not errors else ("PARTIALLY_LOADED" if results else "FAILED")
        mark_batch_status(session, batch, status)

        return {
            "batch_id": str(batch.batch_id),
            "status": status,
            "rows_loaded": results,
            "errors": errors,
        }
    finally:
        session.close()


if __name__ == "__main__":
    summary = run_extraction()
    print("\nExtraction complete:")
    print(f"  batch_id: {summary['batch_id']}")
    print(f"  status:   {summary['status']}")
    print("  rows loaded per source:")
    for source, count in summary["rows_loaded"].items():
        print(f"    {source}: {count}")
    if summary["errors"]:
        print("  errors:")
        for source, msg in summary["errors"].items():
            print(f"    {source}: {msg}")
