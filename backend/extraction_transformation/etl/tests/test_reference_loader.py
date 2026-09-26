from pathlib import Path

from etl.transformation.address_standardizer import load_reference_map, standardize_address
from etl.transformation.reference_loader import load_trust_hierarchy, load_reference_address
from etl.transformation.models import TrustHierarchy

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_reference_address_populates_table_and_is_queryable(session):
    count = load_reference_address(session, FIXTURES / "small_reference_data.csv")
    assert count == 2

    ref_map = load_reference_map(session)
    assert standardize_address("12 MG St.", ref_map) == "12 MG Street"


def test_load_reference_address_upserts_on_rerun(session):
    """Running it twice must not create duplicate rows or fail -- it's config,
    meant to be safely re-loaded every pipeline run."""
    load_reference_address(session, FIXTURES / "small_reference_data.csv")
    count_second_run = load_reference_address(session, FIXTURES / "small_reference_data.csv")
    assert count_second_run == 2

    ref_map = load_reference_map(session)
    assert len(set(ref_map.values())) == 2  # still just 2 distinct long forms


def test_load_trust_hierarchy_handles_leading_explanatory_text(session):
    """The real trust_hierarchy.json has an explanatory sentence before the
    JSON object -- this must not break parsing."""
    count = load_trust_hierarchy(session, FIXTURES / "small_trust_hierarchy.json")
    assert count > 0

    rows = session.query(TrustHierarchy).filter(TrustHierarchy.field_name == "Email").all()
    priorities = {row.source_system: row.priority for row in rows}
    assert priorities["SourceB"] == 1  # SourceB wins for Email per the fixture
    assert priorities["SourceA"] == 2
