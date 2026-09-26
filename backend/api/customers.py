from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from extraction.etl.ingestion.db import get_session
from schemas.customer import CustomerResponse, CustomersResponse


router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"],
)


def get_db():
    db = get_session()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "",
    response_model=CustomersResponse,
    summary="Get all master customers",
)
def get_customers(db: Session = Depends(get_db)):

    query = text(
        """
        SELECT
            master_customer_id,
            name,
            email,
            phone,
            dob,
            address,
            quality_score
        FROM master.master_customer
        ORDER BY created_at DESC
        """
    )

    result = db.execute(query)

    customers = [
        CustomerResponse(
            master_customer_id=row.master_customer_id,
            name=row.name,
            email=row.email,
            phone=row.phone,
            dob=row.dob,
            address=row.address,
            quality_score=row.quality_score,
        )
        for row in result
    ]

    return CustomersResponse(customers=customers)