#!/usr/bin/env python3
"""
Runs identity resolution (matching) + survivorship + product/transaction
linking on the current staging.* data, and persists everything into
master.* -- master_customer, identity_map, field_lineage, core_product,
credit_card_product, loan_product, and customer_transaction.

Run scripts/run_extraction.py and scripts/run_transformation.py first --
this reads whatever is currently staged.

    python scripts/run_matching_and_survivorship.py
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from etl.ingestion.db import get_session  # noqa: E402
from etl.master.customer_loader import persist_golden_customer  # noqa: E402
from etl.master.transaction_loader import link_transactions  # noqa: E402
from etl.matching.identity_resolver import resolve_identities  # noqa: E402
from etl.survivorship.hierarchy_loader import load_hierarchy  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main(threshold=0.85):
    session = get_session()

    try:
        hierarchy = load_hierarchy(session)
        clusters = resolve_identities(session, threshold=threshold)

        match_type_counts = {"exact_email": 0, "exact_phone": 0, "fuzzy_name_address": 0, "unmatched": 0}

        for cluster in clusters:
            persist_golden_customer(
                session,
                cluster["records"],
                hierarchy,
                match_info=cluster["match_info"],
            )
            for match_type, _score in cluster["match_info"].values():
                match_type_counts[match_type] += 1

        print(f"\nMatching + survivorship complete:")
        print(f"  source records processed: {sum(len(c['records']) for c in clusters)}")
        print(f"  golden customers created: {len(clusters)}")
        print(f"  match evidence breakdown (per source record):")
        for match_type, count in match_type_counts.items():
            print(f"    {match_type}: {count}")

        txn_summary = link_transactions(session)
        print(f"\nTransaction linking complete:")
        print(f"  linked:     {txn_summary['linked']}")
        print(f"  unresolved: {txn_summary['unresolved']}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
