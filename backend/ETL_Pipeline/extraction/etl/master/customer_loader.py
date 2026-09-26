"""
Persists the output of survivor_engine.build_golden_fields() into the
master schema: one master_customer row, one identity_map row per source
record in the cluster, and one field_lineage row per populated field
(the "Source Trace" the Customer 360 UI needs).
"""

import logging

from etl.master.models import FieldLineage, IdentityMap, MasterCustomer
from etl.master.product_loader import link_products
from etl.survivorship.survivor_engine import build_golden_fields, quality_score

logger = logging.getLogger(__name__)


def persist_golden_customer(session, cluster_records, hierarchy, match_type="exact", match_info=None):
    """
    cluster_records: list of dicts (one per source record in this cluster),
        each with name/email/phone/dob/address/source_system/source_record_id.
    hierarchy: output of hierarchy_loader.load_hierarchy().
    match_type: fallback recorded on every identity_map row when match_info
        isn't given (e.g. "exact", "fuzzy", "manual", or "ground_truth" for
        validation runs).
    match_info: optional {source_record_id: (match_type, match_score)} --
        when given (as identity_resolver.build_clusters() produces), each
        record's OWN match_type/match_score is used instead of the single
        `match_type` fallback, since different records in the same cluster
        can have been linked in by different rules.

    Returns the created MasterCustomer object.
    """
    golden_fields = build_golden_fields(cluster_records, hierarchy)
    score = quality_score(golden_fields)

    customer = MasterCustomer(
        name=golden_fields["name"]["value"],
        email=golden_fields["email"]["value"],
        phone=golden_fields["phone"]["value"],
        dob=golden_fields["dob"]["value"],
        address=golden_fields["address"]["value"],
        quality_score=score,
    )
    session.add(customer)
    session.flush()  # populates customer.master_customer_id from gen_random_uuid()

    for rec in cluster_records:
        record_match_type, record_match_score = (
            match_info.get(rec["source_record_id"], (match_type, None))
            if match_info else (match_type, None)
        )
        session.add(IdentityMap(
            master_customer_id=customer.master_customer_id,
            source_system=rec["source_system"],
            source_customer_id=rec["source_record_id"],
            match_type=record_match_type,
            match_score=record_match_score,
        ))

    for field_name, info in golden_fields.items():
        if info["value"] is None:
            continue
        session.add(FieldLineage(
            master_customer_id=customer.master_customer_id,
            field_name=field_name,
            source_system=info["source_system"],
            source_customer_id=info["source_record_id"],
            source_value=str(info["value"]),
        ))

    session.commit()
    logger.info(
        "Persisted Golden Customer %s (quality_score=%s) from %d source records",
        customer.master_customer_id, score, len(cluster_records),
    )

    product_counts = link_products(session, customer.master_customer_id, cluster_records)
    session.commit()
    logger.info(
        "Linked products for %s: core=%d credit_card=%d loan=%d",
        customer.master_customer_id, product_counts["core"], product_counts["credit_card"], product_counts["loan"],
    )

    return customer
