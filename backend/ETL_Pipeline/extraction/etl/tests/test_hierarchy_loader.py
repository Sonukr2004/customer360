from pathlib import Path

from etl.survivorship.hierarchy_loader import load_hierarchy
from etl.transformation.reference_loader import load_trust_hierarchy

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_hierarchy_reads_back_what_was_loaded(session):
    load_trust_hierarchy(session, FIXTURES / "small_trust_hierarchy.json")

    hierarchy = load_hierarchy(session)

    assert hierarchy["Email"]["SourceB"] == 1
    assert hierarchy["Email"]["SourceA"] == 2
    assert hierarchy["Phone"]["SourceA"] == 1


def test_load_hierarchy_covers_every_field_in_the_config(session):
    load_trust_hierarchy(session, FIXTURES / "small_trust_hierarchy.json")
    hierarchy = load_hierarchy(session)
    assert set(hierarchy.keys()) == {"Phone", "Email", "Name", "Address", "DOB"}
