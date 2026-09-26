from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ETL_Pipeline.extraction.etl.ingestion.db import get_session

from schemas.customer import CustomerResponse, CustomersResponse
from schemas.customer_detail import (
    AuditLogResponse,
    AuditLogsResponse,
    CoreProductResponse,
    CreditCardProductResponse,
    Customer360Response,
    CustomerDetail,
    CustomerUpdateRequest,
    CustomerUpdateResponse,
    FieldLineageResponse,
    IdentityMatchResponse,
    LoanProductResponse,
    TransactionResponse,
)


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


# ============================================================
# GET /api/customers
# Existing customer list + search
# ============================================================

@router.get(
    "",
    response_model=CustomersResponse,
    summary="Get master customers",
)
def get_customers(
    search: str | None = Query(
        default=None,
        description="Search customers by name, email, or phone",
    ),
    db: Session = Depends(get_db),
):
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


# ============================================================
# GET /api/customers/{customer_id}
# Customer 360
# ============================================================

@router.get(
    "/{customer_id}",
    response_model=Customer360Response,
    summary="Get Customer 360 profile",
)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. Golden Record
    # --------------------------------------------------------

    customer_query = text(
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
        WHERE master_customer_id = :customer_id
        """
    )

    customer = db.execute(
        customer_query,
        {"customer_id": customer_id},
    ).mappings().first()

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    customer_data = CustomerDetail(
        master_customer_id=customer["master_customer_id"],
        name=customer["name"],
        email=customer["email"],
        phone=customer["phone"],
        dob=customer["dob"],
        address=customer["address"],
        quality_score=customer["quality_score"],
    )

    # --------------------------------------------------------
    # 2. Field Lineage
    # --------------------------------------------------------

    lineage_query = text(
        """
        SELECT
            lineage_id,
            field_name,
            source_system,
            source_customer_id,
            source_value
        FROM master.field_lineage
        WHERE master_customer_id = :customer_id
        ORDER BY field_name
        """
    )

    lineage_rows = db.execute(
        lineage_query,
        {"customer_id": customer_id},
    ).mappings().all()

    lineage = [
        FieldLineageResponse(
            lineage_id=row["lineage_id"],
            field_name=row["field_name"],
            source_system=row["source_system"],
            source_customer_id=row["source_customer_id"],
            source_value=row["source_value"],
        )
        for row in lineage_rows
    ]

    # --------------------------------------------------------
    # 3. Core Banking Products
    # --------------------------------------------------------

    core_query = text(
        """
        SELECT
            core_product_id,
            source_system,
            source_customer_id,
            account_id,
            account_type
        FROM master.core_product
        WHERE master_customer_id = :customer_id
        ORDER BY created_at DESC
        """
    )

    core_rows = db.execute(
        core_query,
        {"customer_id": customer_id},
    ).mappings().all()

    core_products = [
        CoreProductResponse(
            core_product_id=row["core_product_id"],
            source_system=row["source_system"],
            source_customer_id=row["source_customer_id"],
            account_id=row["account_id"],
            account_type=row["account_type"],
        )
        for row in core_rows
    ]

    # --------------------------------------------------------
    # 4. Credit Card Products
    # --------------------------------------------------------

    credit_card_query = text(
        """
        SELECT
            credit_card_product_id,
            source_system,
            source_customer_id,
            account_id,
            credit_limit
        FROM master.credit_card_product
        WHERE master_customer_id = :customer_id
        ORDER BY created_at DESC
        """
    )

    credit_card_rows = db.execute(
        credit_card_query,
        {"customer_id": customer_id},
    ).mappings().all()

    credit_card_products = [
        CreditCardProductResponse(
            credit_card_product_id=row["credit_card_product_id"],
            source_system=row["source_system"],
            source_customer_id=row["source_customer_id"],
            account_id=row["account_id"],
            credit_limit=row["credit_limit"],
        )
        for row in credit_card_rows
    ]

    # --------------------------------------------------------
    # 5. Loan Products
    # --------------------------------------------------------

    loan_query = text(
        """
        SELECT
            loan_product_id,
            source_system,
            source_customer_id,
            loan_amount
        FROM master.loan_product
        WHERE master_customer_id = :customer_id
        ORDER BY created_at DESC
        """
    )

    loan_rows = db.execute(
        loan_query,
        {"customer_id": customer_id},
    ).mappings().all()

    loan_products = [
        LoanProductResponse(
            loan_product_id=row["loan_product_id"],
            source_system=row["source_system"],
            source_customer_id=row["source_customer_id"],
            loan_amount=row["loan_amount"],
        )
        for row in loan_rows
    ]

    # --------------------------------------------------------
    # 6. Transactions
    #
    # Transactions do not directly contain master_customer_id.
    # We therefore resolve the customer through the three
    # possible product relationships.
    # --------------------------------------------------------

    transaction_query = text(
        """
        SELECT
            t.transaction_id,
            t.txn_id,
            t.account_id,
            t.source_system,
            t.amount,
            t.transaction_date,
            t.transaction_type,
            'core' AS product_type
        FROM master.customer_transaction t
        INNER JOIN master.core_product p
            ON t.core_product_id = p.core_product_id
        WHERE p.master_customer_id = :customer_id

        UNION ALL

        SELECT
            t.transaction_id,
            t.txn_id,
            t.account_id,
            t.source_system,
            t.amount,
            t.transaction_date,
            t.transaction_type,
            'credit_card' AS product_type
        FROM master.customer_transaction t
        INNER JOIN master.credit_card_product p
            ON t.credit_card_product_id = p.credit_card_product_id
        WHERE p.master_customer_id = :customer_id

        UNION ALL

        SELECT
            t.transaction_id,
            t.txn_id,
            t.account_id,
            t.source_system,
            t.amount,
            t.transaction_date,
            t.transaction_type,
            'loan' AS product_type
        FROM master.customer_transaction t
        INNER JOIN master.loan_product p
            ON t.loan_product_id = p.loan_product_id
        WHERE p.master_customer_id = :customer_id

        ORDER BY transaction_date DESC
        """
    )

    transaction_rows = db.execute(
        transaction_query,
        {"customer_id": customer_id},
    ).mappings().all()

    transactions = [
        TransactionResponse(
            transaction_id=row["transaction_id"],
            txn_id=row["txn_id"],
            account_id=row["account_id"],
            source_system=row["source_system"],
            amount=row["amount"],
            transaction_date=row["transaction_date"],
            transaction_type=row["transaction_type"],
            product_type=row["product_type"],
        )
        for row in transaction_rows
    ]

    # --------------------------------------------------------
    # 7. Identity Matches
    # --------------------------------------------------------

    identity_query = text(
        """
        SELECT
            identity_map_id,
            source_system,
            source_customer_id,
            match_type,
            match_score,
            matched_at
        FROM master.identity_map
        WHERE master_customer_id = :customer_id
        ORDER BY matched_at DESC
        """
    )

    identity_rows = db.execute(
        identity_query,
        {"customer_id": customer_id},
    ).mappings().all()

    identity_matches = [
        IdentityMatchResponse(
            identity_map_id=row["identity_map_id"],
            source_system=row["source_system"],
            source_customer_id=row["source_customer_id"],
            match_type=row["match_type"],
            match_score=row["match_score"],
            matched_at=row["matched_at"],
        )
        for row in identity_rows
    ]

    # --------------------------------------------------------
    # 8. Final Customer 360 response
    # --------------------------------------------------------

    return Customer360Response(
        customer=customer_data,
        lineage=lineage,
        products={
            "core": core_products,
            "credit_cards": credit_card_products,
            "loans": loan_products,
        },
        transactions=transactions,
        identity_matches=identity_matches,
    )


# ============================================================
# PATCH /api/customers/{customer_id}
# Manual Data Steward Override
# ============================================================

@router.patch(
    "/{customer_id}",
    response_model=CustomerUpdateResponse,
    summary="Manually update a Golden Record field",
)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdateRequest,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Convert request into only the fields actually supplied.
    # changed_by is metadata, not a customer field.
    # --------------------------------------------------------

    update_data = payload.model_dump(
        exclude_unset=True,
        exclude={"changed_by"},
    )

    changed_by = payload.changed_by or "Data Steward"

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="At least one customer field must be provided",
        )

    allowed_fields = {
        "name",
        "email",
        "phone",
        "dob",
        "address",
    }

    invalid_fields = set(update_data.keys()) - allowed_fields

    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields: {', '.join(sorted(invalid_fields))}",
        )

    # --------------------------------------------------------
    # Get existing customer
    # --------------------------------------------------------

    existing_query = text(
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
        WHERE master_customer_id = :customer_id
        """
    )

    existing = db.execute(
        existing_query,
        {"customer_id": customer_id},
    ).mappings().first()

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    try:
        # ----------------------------------------------------
        # Update every supplied field and create its audit log.
        # Both happen in the same database transaction.
        # ----------------------------------------------------

        for field_name, new_value in update_data.items():

            old_value = existing[field_name]

            # Convert values to strings for audit_log.text columns.
            old_value_text = (
                old_value.isoformat()
                if old_value is not None and hasattr(old_value, "isoformat")
                else str(old_value)
                if old_value is not None
                else None
            )

            new_value_text = (
                new_value.isoformat()
                if new_value is not None and hasattr(new_value, "isoformat")
                else str(new_value)
                if new_value is not None
                else None
            )

            # Skip audit/update if the value hasn't changed.
            if old_value_text == new_value_text:
                continue

            update_query = text(
                f"""
                UPDATE master.master_customer
                SET
                    {field_name} = :new_value,
                    updated_at = now()
                WHERE master_customer_id = :customer_id
                """
            )

            db.execute(
                update_query,
                {
                    "new_value": new_value,
                    "customer_id": customer_id,
                },
            )

            audit_query = text(
                """
                INSERT INTO master.audit_log (
                    master_customer_id,
                    field_name,
                    old_value,
                    new_value,
                    changed_by,
                    action
                )
                VALUES (
                    :customer_id,
                    :field_name,
                    :old_value,
                    :new_value,
                    :changed_by,
                    'UPDATE'
                )
                """
            )

            db.execute(
                audit_query,
                {
                    "customer_id": customer_id,
                    "field_name": field_name,
                    "old_value": old_value_text,
                    "new_value": new_value_text,
                    "changed_by": changed_by,
                },
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    # --------------------------------------------------------
    # Return the updated customer
    # --------------------------------------------------------

    updated = db.execute(
        existing_query,
        {"customer_id": customer_id},
    ).mappings().first()

    return CustomerUpdateResponse(
        message="Customer updated successfully",
        customer=CustomerDetail(
            master_customer_id=updated["master_customer_id"],
            name=updated["name"],
            email=updated["email"],
            phone=updated["phone"],
            dob=updated["dob"],
            address=updated["address"],
            quality_score=updated["quality_score"],
        ),
    )


# ============================================================
# GET /api/customers/{customer_id}/audit
# ============================================================

@router.get(
    "/{customer_id}/audit",
    response_model=AuditLogsResponse,
    summary="Get customer audit history",
)
def get_customer_audit(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    # First make sure customer exists.
    customer_exists_query = text(
        """
        SELECT 1
        FROM master.master_customer
        WHERE master_customer_id = :customer_id
        """
    )

    customer_exists = db.execute(
        customer_exists_query,
        {"customer_id": customer_id},
    ).first()

    if customer_exists is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    audit_query = text(
        """
        SELECT
            audit_id,
            field_name,
            old_value,
            new_value,
            changed_by,
            changed_at,
            action
        FROM master.audit_log
        WHERE master_customer_id = :customer_id
        ORDER BY changed_at DESC, audit_id DESC
        """
    )

    audit_rows = db.execute(
        audit_query,
        {"customer_id": customer_id},
    ).mappings().all()

    audit_logs = [
        AuditLogResponse(
            audit_id=row["audit_id"],
            field_name=row["field_name"],
            old_value=row["old_value"],
            new_value=row["new_value"],
            changed_by=row["changed_by"],
            changed_at=row["changed_at"],
            action=row["action"],
        )
        for row in audit_rows
    ]

    return AuditLogsResponse(
        audit_logs=audit_logs
    )