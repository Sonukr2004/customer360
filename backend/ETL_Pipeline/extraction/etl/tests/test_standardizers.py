from etl.transformation.address_standardizer import standardize_address
from etl.transformation.email_standardizer import standardize_email
from etl.transformation.name_standardizer import standardize_name
from etl.transformation.phone_standardizer import standardize_phone


# --- name ---

def test_standardize_name_proper_case():
    assert standardize_name("JOHN doe") == "John Doe"


def test_standardize_name_trims_and_collapses_spaces():
    assert standardize_name("  john   doe  ") == "John Doe"


def test_standardize_name_null_input():
    assert standardize_name(None) is None
    assert standardize_name("") is None
    assert standardize_name("   ") is None


# --- email ---

def test_standardize_email_lowercases_and_trims():
    assert standardize_email(" JOHN@GMAIL.COM ") == "john@gmail.com"


def test_standardize_email_null_input():
    assert standardize_email(None) is None
    assert standardize_email("") is None


# --- phone ---

def test_standardize_phone_strips_formatting_keeps_country_code():
    assert standardize_phone("+91 98765-43210") == "919876543210"


def test_standardize_phone_plain_ten_digit_unchanged():
    assert standardize_phone("9876543210") == "9876543210"


def test_standardize_phone_null_input():
    assert standardize_phone(None) is None
    assert standardize_phone("") is None


# --- address (using an in-memory ref_map, not the DB -- DB-backed lookup
#     is covered by test_address_standardizer_db.py) ---

def test_standardize_address_replaces_abbreviations():
    ref_map = {"st.": "Street", "st": "Street", "rd.": "Road", "rd": "Road"}
    assert standardize_address("12 MG St.", ref_map) == "12 MG Street"
    assert standardize_address("45 Park Rd", ref_map) == "45 Park Road"


def test_standardize_address_does_not_mangle_full_words():
    ref_map = {"st.": "Street", "st": "Street"}
    assert standardize_address("1 Street Lane", ref_map) == "1 Street Lane"


def test_standardize_address_null_input():
    ref_map = {"st.": "Street"}
    assert standardize_address(None, ref_map) is None
