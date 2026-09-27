from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.customers import get_db


router = APIRouter(
    prefix="/api/quality",
    tags=["Data Quality"],
)


@router.get("")
def get_quality_data(
    db: Session = Depends(get_db),
):
    query = text(
        """
        SELECT
            identity_map_id,
            master_customer_id,
            source_system,
            source_customer_id,
            match_type,
            match_score,
            matched_at
        FROM master.identity_map
        ORDER BY matched_at DESC, identity_map_id DESC
        """
    )

    rows = db.execute(query).mappings().all()

    matches = []

    for row in rows:
        matches.append(
            {
                "identity_map_id": row["identity_map_id"],
                "master_customer_id": str(
                    row["master_customer_id"]
                ),
                "source_system": row["source_system"],
                "source_customer_id": row["source_customer_id"],
                "match_type": row["match_type"],
                "match_score": (
                    float(row["match_score"])
                    if row["match_score"] is not None
                    else None
                ),
                "matched_at": row["matched_at"],
            }
        )

    return {
        "total_matches": len(matches),
        "matches": matches,
    }