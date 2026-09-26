from etl.master.transaction_loader import _account_id_to_source


def test_account_id_credit_card_prefix():
    assert _account_id_to_source("CC_100") == "SourceB"


def test_account_id_loan_prefix():
    assert _account_id_to_source("L_500") == "SourceC"


def test_account_id_default_is_core_banking():
    assert _account_id_to_source("C0001") == "SourceA"
