"""
Loads the reference/config files into reference.reference_address and
reference.trust_hierarchy. These are config tables, not per-batch data --
this is idempotent (upsert), safe to run every time the pipeline runs.
"""

import csv
import json
import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert

from etl.transformation.models import ReferenceAddress, TrustHierarchy

logger = logging.getLogger(__name__)


def load_reference_address(session, file_path):
    """
    Loads reference_data.csv (Short_Form, Long_Form) into
    reference.reference_address, upserting on short_form.
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [row for row in reader if len(row) >= 2]

    # Skip a header row if present ("Short_Form, Long_Form")
    if rows and rows[0][0].strip().lower() in ("short_form", "short form"):
        rows = rows[1:]

    count = 0
    for short_form, long_form in rows:
        stmt = pg_insert(ReferenceAddress).values(
            short_form=short_form.strip(), long_form=long_form.strip()
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["short_form"], set_={"long_form": stmt.excluded.long_form}
        )
        session.execute(stmt)
        count += 1

    session.commit()
    logger.info("Upserted %d rows into reference.reference_address", count)
    return count


def load_trust_hierarchy(session, file_path):
    """
    Loads trust_hierarchy.json into reference.trust_hierarchy, upserting on
    (field_name, source_system). The provided file has an explanatory text
    line BEFORE the JSON object, so this extracts the {...} block rather
    than assuming the file is pure JSON.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    start = content.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in {file_path}")
    config = json.loads(content[start:])

    count = 0
    for field_name, source_order in config.get("field_priorities", {}).items():
        for priority, source_system in enumerate(source_order, start=1):
            stmt = pg_insert(TrustHierarchy).values(
                field_name=field_name, source_system=source_system, priority=priority
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["field_name", "source_system"],
                set_={"priority": stmt.excluded.priority},
            )
            session.execute(stmt)
            count += 1

    session.commit()
    logger.info("Upserted %d rows into reference.trust_hierarchy", count)
    return count
