from etl.survivorship.survivor_engine import build_golden_fields, quality_score, resolve_field

HIERARCHY = {
    "Phone": {"SourceA": 1, "SourceB": 2, "SourceC": 3},
    "Email": {"SourceB": 1, "SourceA": 2, "SourceC": 3},
    "Name": {"SourceA": 1, "SourceB": 2, "SourceC": 3},
    "Address": {"SourceB": 1, "SourceA": 2, "SourceC": 3},
    "DOB": {"SourceA": 1, "SourceB": 2, "SourceC": 3},
}


def test_resolve_field_picks_highest_priority_source():
    candidates = [("SourceA", "a@old.com", "A1"), ("SourceB", "b@new.com", "B1")]
    value, source, rid = resolve_field("Email", candidates, HIERARCHY["Email"])
    assert (value, source, rid) == ("b@new.com", "SourceB", "B1")  # SourceB wins Email


def test_resolve_field_is_field_specific_not_source_specific():
    """The SAME cluster must let different sources win different fields --
    there is no single 'most trusted source overall'."""
    email_candidates = [("SourceA", "a@x.com", "A1"), ("SourceB", "b@x.com", "B1")]
    phone_candidates = [("SourceA", "111", "A1"), ("SourceB", "222", "B1")]

    _, email_winner, _ = resolve_field("Email", email_candidates, HIERARCHY["Email"])
    _, phone_winner, _ = resolve_field("Phone", phone_candidates, HIERARCHY["Phone"])

    assert email_winner == "SourceB"  # Email hierarchy: B > A
    assert phone_winner == "SourceA"  # Phone hierarchy: A > B


def test_resolve_field_skips_null_candidates_regardless_of_priority():
    """SourceA is top priority for Phone, but has no phone here -- SourceC
    (lowest priority) must still win rather than the field going null."""
    candidates = [("SourceA", None, "A1"), ("SourceB", None, "B1"), ("SourceC", "999", "C1")]
    value, source, rid = resolve_field("Phone", candidates, HIERARCHY["Phone"])
    assert (value, source, rid) == ("999", "SourceC", "C1")


def test_resolve_field_returns_none_when_every_candidate_is_null():
    candidates = [("SourceA", None, "A1"), ("SourceB", None, "B1")]
    assert resolve_field("Email", candidates, HIERARCHY["Email"]) == (None, None, None)


def test_resolve_field_treats_unranked_source_as_lowest_priority():
    """A source with no entry in this field's hierarchy must not crash --
    it just loses to any ranked source, even one with a worse-sounding rank."""
    candidates = [("SourceD", "unranked@x.com", "D1"), ("SourceC", "c@x.com", "C1")]
    value, source, rid = resolve_field("Email", candidates, HIERARCHY["Email"])
    assert source == "SourceC"  # SourceC is ranked (3); SourceD isn't ranked at all


def test_build_golden_fields_end_to_end_mixed_winners():
    cluster = [
        {
            "source_system": "SourceA",
            "source_record_id": "A1",
            "name": "John Doe",
            "email": "john.old@example.com",
            "phone": "1111111111",
            "dob": "1990-01-01",
            "address": "1 Old Street",
        },
        {
            "source_system": "SourceB",
            "source_record_id": "B1",
            "name": "J Doe",
            "email": "john.new@example.com",
            "phone": None,
            "dob": None,
            "address": "1 New Street",
        },
    ]
    golden = build_golden_fields(cluster, HIERARCHY)

    assert golden["email"]["value"] == "john.new@example.com"  # SourceB wins Email
    assert golden["email"]["source_system"] == "SourceB"
    assert golden["phone"]["value"] == "1111111111"  # only SourceA has phone
    assert golden["phone"]["source_system"] == "SourceA"
    assert golden["address"]["value"] == "1 New Street"  # SourceB wins Address
    assert golden["dob"]["value"] == "1990-01-01"  # only SourceA has DOB
    assert golden["name"]["source_system"] == "SourceA"  # SourceA wins Name


def test_quality_score_all_fields_populated():
    golden = {
        "name": {"value": "John Doe"}, "email": {"value": "j@x.com"},
        "phone": {"value": "123"}, "dob": {"value": "1990-01-01"}, "address": {"value": "1 St"},
    }
    assert quality_score(golden) == 100


def test_quality_score_partial():
    golden = {
        "name": {"value": "John Doe"}, "email": {"value": None},
        "phone": {"value": "123"}, "dob": {"value": None}, "address": {"value": None},
    }
    assert quality_score(golden) == 40  # 2 of 5 fields populated
