"""
Manual override: the ONLY sanctioned way master_customer changes outside
of a pipeline run. Updates the Golden Record field, updates field_lineage
to reflect the override (source_system becomes "DataSteward", not a real
source system), and appends an audit_log row recording who changed what
and when.

This is what the PS's Data Stewardship / audit-trail requirement is
actually asking for -- until the API layer wires this to a UI, this is
the callable that will sit behind the PATCH endpoint.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import text

logger = logging.getLogger(__name__)

ALLOWED_FIELDS = {"name", "email", "phone", "dob", "address"}


class CustomerNotFoundError(Exception):
    pass


class InvalidFieldError(Exception):
    pass


def override_field(session, master_customer_id, field_name, new_value, changed_by="data_steward"):
    """
    Updates one field on master_customer, records the change in audit_log,
    and updates field_lineage to show the override (rather than a source
    system) as the new value's origin.

    Returns (old_value, new_value).
    """
    if field_name not in ALLOWED_FIELDS:
        raise InvalidFieldError(f"'{field_name}' is not an overridable field")

    row = session.execute(text(
        f"SELECT {field_name} FROM master.master_customer WHERE master_customer_id = :cid"
    ), {"cid": master_customer_id}).fetchone()

    if row is None:
        raise CustomerNotFoundError(f"Customer {master_customer_id} not found")

    old_value = row[0]

    session.execute(text(
        f"UPDATE master.master_customer SET {field_name} = :new_value, updated_at = NOW() "
        f"WHERE master_customer_id = :cid"
    ), {"new_value": new_value, "cid": master_customer_id})

    # field_lineage tracks "where did this value come from" -- an override
    # replaces whatever source used to be recorded there.
    existing_lineage = session.execute(text(
        "SELECT lineage_id FROM master.field_lineage "
        "WHERE master_customer_id = :cid AND field_name = :field"
    ), {"cid": master_customer_id, "field": field_name}).fetchone()

    if existing_lineage:
        session.execute(text(
            "UPDATE master.field_lineage "
            "SET source_system = 'DataSteward', source_customer_id = NULL, "
            "    source_value = :new_value, created_at = NOW() "
            "WHERE lineage_id = :lid"
        ), {"new_value": str(new_value), "lid": existing_lineage.lineage_id})
    else:
        session.execute(text(
            "INSERT INTO master.field_lineage "
            "(master_customer_id, field_name, source_system, source_customer_id, source_value) "
            "VALUES (:cid, :field, 'DataSteward', NULL, :new_value)"
        ), {"cid": master_customer_id, "field": field_name, "new_value": str(new_value)})

    session.execute(text(
        "INSERT INTO master.audit_log "
        "(master_customer_id, field_name, old_value, new_value, changed_by, action) "
        "VALUES (:cid, :field, :old_value, :new_value, :changed_by, 'UPDATE')"
    ), {
        "cid": master_customer_id, "field": field_name,
        "old_value": str(old_value) if old_value is not None else None,
        "new_value": str(new_value), "changed_by": changed_by,
    })

    session.commit()
    logger.info(
        "Override: customer %s field '%s' %r -> %r (by %s)",
        master_customer_id, field_name, old_value, new_value, changed_by,
    )
    return old_value, new_value
