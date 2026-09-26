"""
Integration test: runs extraction -> transformation -> identity resolution
on small fixture data, and verifies the actual clusters formed.

Fixture data (see etl/tests/fixtures/small_*): 2 core banking records
(C0001 John Doe, C0002 Jane Roe), 1 credit card (CC_100, same email as
C0001), 1 loan (L_500, same phone as C0001). Expected: C0001+CC_100+L_500
merge into one cluster (email C0001<->CC_100, phone C0001<->L_500);
C0002 has no match and stays a singleton.
"""

from pathlib import Path

from etl.ingestion.extract import run_extraction
from etl.ingestion.loader import load_core_banking, load_credit_card, load_loan, load_transactions
from etl.matching.identity_resolver import resolve_identities
from etl.transformation.transform import run_transformation

FIXTURES = Path(__file__).parent / "fixtures"

SMALL_SOURCES = [
    ("core_banking", FIXTURES / "small_core_banking.csv", load_core_banking),
    ("credit_card", FIXTURES / "small_credit_card.csv", load_credit_card),
    ("loan", FIXTURES / "small_loan.jsonl", load_loan),
    ("transaction", FIXTURES / "small_transactions.csv", load_transactions),
]


def _stage_fixture_data(session):
    run_extraction(sources=SMALL_SOURCES)
    run_transformation(
        session=session,
        reference_file=FIXTURES / "small_reference_data.csv",
        hierarchy_file=FIXTURES / "small_trust_hierarchy.json",
    )


def test_resolve_identities_produces_expected_cluster_count(session):
    _stage_fixture_data(session)
    clusters = resolve_identities(session, threshold=0.85)

    # C0001+CC_100+L_500 (John Doe) merge; C0002 (Jane Roe) is a singleton
    assert len(clusters) == 2

    cluster_sizes = sorted(len(c["records"]) for c in clusters)
    assert cluster_sizes == [1, 3]


def test_resolve_identities_merges_john_doe_cluster_with_correct_match_types(session):
    _stage_fixture_data(session)
    clusters = resolve_identities(session, threshold=0.85)

    john_cluster = next(c for c in clusters if len(c["records"]) == 3)
    record_ids = {r["source_record_id"] for r in john_cluster["records"]}
    assert record_ids == {"C0001", "CC_100", "L_500"}

    # C0001<->CC_100 via email, C0001<->L_500 via phone
    assert john_cluster["match_info"]["C0001"][0] in ("exact_email", "exact_phone")
    assert john_cluster["match_info"]["CC_100"][0] == "exact_email"
    assert john_cluster["match_info"]["L_500"][0] == "exact_phone"


def test_resolve_identities_gives_singleton_unmatched_status(session):
    _stage_fixture_data(session)
    clusters = resolve_identities(session, threshold=0.85)

    singleton = next(c for c in clusters if len(c["records"]) == 1)
    assert singleton["records"][0]["source_record_id"] == "C0002"
    assert singleton["match_info"]["C0002"] == ("unmatched", None)
