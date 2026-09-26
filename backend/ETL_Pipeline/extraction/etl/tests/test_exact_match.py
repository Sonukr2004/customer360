from etl.matching.exact_match import match_by_email, match_by_phone
from etl.matching.identity_resolver import UnionFind


def _rec(source, rid, **fields):
    return {"source_system": source, "source_record_id": rid, **fields}


def test_match_by_email_links_two_different_sources():
    records = [
        _rec("SourceA", "A1", email="john@x.com"),
        _rec("SourceB", "B1", email="john@x.com"),
    ]
    uf = UnionFind(2)
    edges = match_by_email(records, uf)
    assert uf.find(0) == uf.find(1)
    assert edges == [(0, 1, "exact_email")]


def test_match_by_email_ignores_same_source_pairs():
    """Two rows from the SAME source sharing an email is a duplicate-ID
    data quality issue, not an identity match -- must not union."""
    records = [
        _rec("SourceA", "A1", email="dup@x.com"),
        _rec("SourceA", "A2", email="dup@x.com"),
    ]
    uf = UnionFind(2)
    edges = match_by_email(records, uf)
    assert uf.find(0) != uf.find(1)
    assert edges == []


def test_match_by_email_ignores_null_values():
    records = [_rec("SourceA", "A1", email=None), _rec("SourceB", "B1", email=None)]
    uf = UnionFind(2)
    assert match_by_email(records, uf) == []


def test_match_by_phone_links_two_different_sources():
    records = [
        _rec("SourceA", "A1", phone="9876543210"),
        _rec("SourceC", "C1", phone="9876543210"),
    ]
    uf = UnionFind(2)
    edges = match_by_phone(records, uf)
    assert uf.find(0) == uf.find(1)
    assert edges == [(0, 1, "exact_phone")]


def test_different_people_are_not_linked():
    records = [
        _rec("SourceA", "A1", email="alice@x.com", phone="1111111111"),
        _rec("SourceB", "B1", email="bob@x.com", phone="2222222222"),
    ]
    uf = UnionFind(2)
    match_by_email(records, uf)
    match_by_phone(records, uf)
    assert uf.find(0) != uf.find(1)
