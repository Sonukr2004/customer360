"""
Duplicate checks: detects when the SAME source system has the SAME
identifier appearing more than once WITHIN A SINGLE BATCH (e.g.
Customer_ID 'C0042' showing up twice in one run of core_banking.csv).

This is scoped per-batch on purpose: landing is append-only, so if
extraction has been run multiple times, the same ID legitimately exists
once per batch across many batches -- that's expected re-runs, not a data
quality problem, and must NOT be flagged. A genuine duplicate is the SAME
ID appearing twice *inside one batch_id*, which usually means a re-issued
ID, a source-system export bug, or a data entry mistake in that specific
load.

This is also distinct from cross-source identity matching (the same real
person appearing as different IDs across Core Banking / Credit Card /
Loan) -- that's the matching stage's job, not this check's.

Rows are NOT dropped or altered here -- this only detects and reports,
since deciding which duplicate row is authoritative isn't a call this
stage should make silently.
"""

import logging
from collections import defaultdict

from sqlalchemy import func

logger = logging.getLogger(__name__)


def find_duplicate_ids(session, model, id_column_name, source_label, batch_id=None):
    """
    Scans `model`'s table, grouped by (batch_id, id_column_name), for
    groups that occur more than once -- i.e. the same ID repeated within
    the SAME batch. NULLs in id_column_name are ignored (a missing ID is
    a validation problem, not a duplicate problem).

    If `batch_id` is given, only that batch is scanned -- this is the
    normal case, since transformation only ever processes one batch at a
    time. Pass batch_id=None only for a deliberate full-history scan.

    Returns {id_value: count} for every ID duplicated within some batch.
    Logs a warning per duplicate found, including which batch it's in.
    """
    id_column = getattr(model, id_column_name)

    query = session.query(model.batch_id, id_column, func.count().label("occurrences")).filter(
        id_column.isnot(None)
    )
    if batch_id is not None:
        query = query.filter(model.batch_id == batch_id)

    rows = query.group_by(model.batch_id, id_column).having(func.count() > 1).all()

    duplicates = defaultdict(int)
    for row_batch_id, id_value, occurrences in rows:
        duplicates[id_value] = max(duplicates[id_value], occurrences)
        logger.warning(
            "Duplicate %s detected in %s (batch %s): %r appears %d times in this batch",
            id_column_name, source_label, row_batch_id, id_value, occurrences,
        )

    return dict(duplicates)
