"""
Links each staging.staging_transaction row to its Golden Customer -- via
the product it belongs to, not directly to master_customer_id, per the
revised schema. This is the specific scenario the PS calls out for
integration testing: transaction_data.csv uses raw source IDs
(Account_ID), and they must resolve to the Golden Record, not stay as
raw IDs.

Account_ID prefix determines source system:
    "CC_..." -> SourceB (Credit Card)
    "L_..."  -> SourceC (Loan)
    otherwise -> SourceA (Core Banking)
"""

import logging

from sqlalchemy import text

from etl.master.product_models import CustomerTransaction

logger = logging.getLogger(__name__)


def _account_id_to_source(account_id):
    if account_id.startswith("CC_"):
        return "SourceB"
    if account_id.startswith("L_"):
        return "SourceC"
    return "SourceA"


def _load_product_lookup(session):
    """
    Returns {(source_system, account_id): (product_type, product_id)}
    across all three product tables, so each transaction can be resolved
    with one dict lookup instead of a query per row.
    """
    lookup = {}

    for row in session.execute(text(
        "SELECT source_system, account_id, core_product_id FROM master.core_product"
    )).fetchall():
        lookup[(row.source_system, row.account_id)] = ("core", row.core_product_id)

    for row in session.execute(text(
        "SELECT source_system, account_id, credit_card_product_id FROM master.credit_card_product"
    )).fetchall():
        lookup[(row.source_system, row.account_id)] = ("credit_card", row.credit_card_product_id)

    # Loan products don't carry an account_id column in the schema -- they're
    # looked up by source_customer_id instead (same value as the loan account).
    for row in session.execute(text(
        "SELECT source_system, source_customer_id, loan_product_id FROM master.loan_product"
    )).fetchall():
        lookup[(row.source_system, row.source_customer_id)] = ("loan", row.loan_product_id)

    return lookup


def link_transactions(session, batch_id=None):
    """
    Reads staging.staging_transaction (optionally scoped to one batch) and
    inserts a master.customer_transaction row per record, with exactly one
    of core_product_id / credit_card_product_id / loan_product_id set.

    Returns {"linked": n, "unresolved": n}. An unresolved transaction
    (Account_ID doesn't match any known product) is NOT inserted into
    master.customer_transaction -- the table's CHECK constraint requires
    exactly one product FK to be set, so there's no valid row to insert --
    but it IS counted and logged, so nothing is silently dropped from view;
    it stays visible in staging.staging_transaction either way.
    """
    batch_filter = "WHERE batch_id = :batch_id" if batch_id else ""
    params = {"batch_id": batch_id} if batch_id else {}

    rows = session.execute(text(f"""
        SELECT txn_id, account_id, amount, transaction_date, transaction_type
        FROM staging.staging_transaction {batch_filter}
    """), params).fetchall()

    product_lookup = _load_product_lookup(session)

    linked, unresolved = 0, 0

    for row in rows:
        source_system = _account_id_to_source(row.account_id)
        product_key = (source_system, row.account_id)
        product_match = product_lookup.get(product_key)

        if product_match is None:
            unresolved += 1
            logger.warning(
                "Unresolved transaction %s: no %s product found for account_id=%r",
                row.txn_id, source_system, row.account_id,
            )
            continue

        product_type, product_id = product_match
        txn = CustomerTransaction(
            txn_id=row.txn_id,
            account_id=row.account_id,
            source_system=source_system,
            amount=row.amount,
            transaction_date=row.transaction_date,
            transaction_type=row.transaction_type,
        )
        if product_type == "core":
            txn.core_product_id = product_id
        elif product_type == "credit_card":
            txn.credit_card_product_id = product_id
        elif product_type == "loan":
            txn.loan_product_id = product_id

        session.add(txn)
        linked += 1

    session.commit()
    logger.info("Linked %d transactions to Golden Customers (%d unresolved).", linked, unresolved)
    return {"linked": linked, "unresolved": unresolved}
