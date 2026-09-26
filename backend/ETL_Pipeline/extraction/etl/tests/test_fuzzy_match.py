from etl.matching.fuzzy_match import match_by_name_address
from etl.matching.identity_resolver import UnionFind


def _rec(source, rid, **fields):
    return {"source_system": source, "source_record_id": rid, **fields}


def test_fuzzy_match_links_similar_name_and_address():
    records = [
        _rec("SourceA", "A1", name="Jon Doe", address="12 MG Street"),
        _rec("SourceB", "B1", name="John Doe", address="12 MG Street"),
    ]
    uf = UnionFind(2)
    edges = match_by_name_address(records, uf, threshold=0.85)
    assert uf.find(0) == uf.find(1)
    assert edges[0][2] == "fuzzy_name_address"


def test_fuzzy_match_rejects_dissimilar_pairs():
    records = [
        _rec("SourceA", "A1", name="Alice Smith", address="1 Oak Street"),
        _rec("SourceB", "B1", name="Bob Jones", address="2 Pine Road"),
    ]
    uf = UnionFind(2)
    match_by_name_address(records, uf, threshold=0.85)
    assert uf.find(0) != uf.find(1)


def test_fuzzy_match_skips_pairs_already_linked_by_an_earlier_rule():
    """If exact email already merged two records, fuzzy must not re-process
    (or double-score) that same pair."""
    records = [
        _rec("SourceA", "A1", name="John Doe", address="12 MG Street"),
        _rec("SourceB", "B1", name="John Doe", address="12 MG Street"),
    ]
    uf = UnionFind(2)
    uf.union(0, 1)  # simulate an earlier exact-match rule already merging these
    edges = match_by_name_address(records, uf, threshold=0.85)
    assert edges == []


def test_fuzzy_match_allowed_within_same_source():
    """Real Core Banking data has its own internal duplicates -- fuzzy
    matching must be able to catch those even though both records share
    a source_system."""
    records = [
        _rec("SourceA", "C0098", name="Ashley Meza", address="12 MG Street"),
        _rec("SourceA", "C1502", name="Ashley Meza", address="12 MG Street"),
    ]
    uf = UnionFind(2)
    match_by_name_address(records, uf, threshold=0.85)
    assert uf.find(0) == uf.find(1)


def test_fuzzy_match_requires_both_name_and_address_to_meet_threshold():
    """Similar name but wildly different address must NOT match -- both
    fields have to independently clear the bar."""
    records = [
        _rec("SourceA", "A1", name="John Doe", address="12 MG Street"),
        _rec("SourceB", "B1", name="John Doe", address="999 Totally Different Ave"),
    ]
    uf = UnionFind(2)
    match_by_name_address(records, uf, threshold=0.85)
    assert uf.find(0) != uf.find(1)


def test_fuzzy_match_skips_pairs_missing_name_or_address():
    records = [
        _rec("SourceA", "A1", name=None, address="12 MG Street"),
        _rec("SourceB", "B1", name="John Doe", address="12 MG Street"),
    ]
    uf = UnionFind(2)
    edges = match_by_name_address(records, uf, threshold=0.85)
    assert edges == []
