from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ETL_Pipeline.extraction.etl.ingestion.db import get_session
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
    summary="Get master customers",
)
def get_customers(
    search: str | None = Query(
        default=None,
        description="Search customers by name, email, or phone",
        examples=["john", "gmail.com", "9876543210"],
    ),
    db: Session = Depends(get_db),
):
    """
    Get master customers.

    If search is provided, the search is performed against:
    - name
    - email
    - phone

    If search is omitted, all customers are returned.
    """

    search = search.strip() if search else None

    if search:
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
            WHERE
                name ILIKE :search_pattern
                OR email ILIKE :search_pattern
                OR phone ILIKE :search_pattern
            ORDER BY created_at DESC
            """
        )

        result = db.execute(
            query,
            {
                "search_pattern": f"%{search}%"
            },
        )

    else:
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