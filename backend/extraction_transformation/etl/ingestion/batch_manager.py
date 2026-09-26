"""
Batch management: every extraction run is one ingestion event, tracked in
landing.landing_batch. All rows loaded during this run are tagged with the
same batch_id, so you can always answer "which upload produced this data?"
"""

import logging

from etl.ingestion.models import LandingBatch

logger = logging.getLogger(__name__)


def create_batch(session, total_files, uploaded_by=None):
    """Creates a new batch row with status UPLOADED and returns the ORM object
    (with batch_id already populated from the DB's gen_random_uuid() default)."""
    batch = LandingBatch(total_files=total_files, uploaded_by=uploaded_by, status="UPLOADED")
    session.add(batch)
    session.flush()  # populates batch.batch_id from the server default
    logger.info("Created batch %s (total_files=%d)", batch.batch_id, total_files)
    return batch


def mark_batch_status(session, batch, status):
    """Updates the batch's status (e.g. LOADED, FAILED) and commits."""
    batch.status = status
    session.commit()
    logger.info("Batch %s marked %s", batch.batch_id, status)
