"""
Creates one product row per source record in a cluster, linked directly
to the Golden Customer -- no customer_product intermediary, per the
revised architecture. A customer with 2 Core Banking records in their
cluster gets 2 core_product rows (e.g. 2 savings accounts).
"""

import logging

from etl.master.product_models import CoreProduct, CreditCardProduct, LoanProduct

logger = logging.getLogger(__name__)


def link_products(session, master_customer_id, cluster_records):
    """
    cluster_records: the same list of dicts passed to persist_golden_customer
    (each with source_system, source_record_id, and -- for credit card/loan
    records -- credit_limit / loan_amt if present).

    Returns counts: {"core": n, "credit_card": n, "loan": n}.
    """
    counts = {"core": 0, "credit_card": 0, "loan": 0}

    for rec in cluster_records:
        if rec["source_system"] == "SourceA":
            session.add(CoreProduct(
                master_customer_id=master_customer_id,
                source_system="SourceA",
                source_customer_id=rec["source_record_id"],
                account_id=rec["source_record_id"],
            ))
            counts["core"] += 1

        elif rec["source_system"] == "SourceB":
            session.add(CreditCardProduct(
                master_customer_id=master_customer_id,
                source_system="SourceB",
                source_customer_id=rec["source_record_id"],
                account_id=rec["source_record_id"],
                credit_limit=rec.get("credit_limit"),
            ))
            counts["credit_card"] += 1

        elif rec["source_system"] == "SourceC":
            session.add(LoanProduct(
                master_customer_id=master_customer_id,
                source_system="SourceC",
                source_customer_id=rec["source_record_id"],
                loan_amount=rec.get("loan_amount"),
            ))
            counts["loan"] += 1

    return counts
