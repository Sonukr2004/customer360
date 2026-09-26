from pathlib import Path

from etl.ingestion.batch_manager import create_batch
from etl.ingestion.loader import load_core_banking
from etl.ingestion.models import LandingCoreBanking
from etl.transformation.duplicate_checker import find_duplicate_ids

FIXTURES = Path(__file__).parent / "fixtures"


def test_find_duplicate_ids_detects_repeated_customer_id(session):
    """C0001 appears twice (once with slightly different data the second
    time) in this fixture -- a classic 're-issued ID' data quality issue."""
    batch = create_batch(session, total_files=1)
    load_core_banking(session, batch, FIXTURES / "core_banking_with_duplicate_id.csv")

    duplicates = find_duplicate_ids(session, LandingCoreBanking, "customer_id", "core_banking")

    assert duplicates == {"C0001": 2}


def test_find_duplicate_ids_returns_empty_when_no_duplicates(session):
    batch = create_batch(session, total_files=1)
    load_core_banking(session, batch, FIXTURES / "small_core_banking.csv")

    duplicates = find_duplicate_ids(session, LandingCoreBanking, "customer_id", "core_banking")

    assert duplicates == {}


def test_transform_run_surfaces_duplicates_without_blocking_the_pipeline(session):
    """A duplicate ID in one source must not stop staging from completing
    for every source -- it's reported, not fatal."""
    from etl.transformation.transform import run_transformation

    batch = create_batch(session, total_files=1)
    load_core_banking(session, batch, FIXTURES / "core_banking_with_duplicate_id.csv")
    session.commit()

    summary = run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )

    assert summary["duplicates_found"]["core_banking"] == {"C0001": 2}
    # Both C0001 rows still land in staging -- detection doesn't drop data
    assert summary["core_banking"] == 3
