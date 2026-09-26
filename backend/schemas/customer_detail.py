from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    master_customer_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    address: Optional[str] = None
    quality_score: Optional[Decimal] = None


class FieldLineageResponse(BaseModel):
    lineage_id: int
    field_name: str
    source_system: Optional[str] = None
    source_customer_id: Optional[str] = None
    source_value: Optional[str] = None


class CoreProductResponse(BaseModel):
    core_product_id: UUID
    source_system: str
    source_customer_id: Optional[str] = None
    account_id: Optional[str] = None
    account_type: Optional[str] = None


class CreditCardProductResponse(BaseModel):
    credit_card_product_id: UUID
    source_system: str
    source_customer_id: Optional[str] = None
    account_id: Optional[str] = None
    credit_limit: Optional[Decimal] = None


class LoanProductResponse(BaseModel):
    loan_product_id: UUID
    source_system: str
    source_customer_id: Optional[str] = None
    loan_amount: Optional[Decimal] = None


class TransactionResponse(BaseModel):
    transaction_id: int
    txn_id: str
    account_id: Optional[str] = None
    source_system: str
    amount: Optional[Decimal] = None
    transaction_date: Optional[date] = None
    transaction_type: Optional[str] = None
    product_type: Optional[str] = None


class IdentityMatchResponse(BaseModel):
    identity_map_id: int
    source_system: str
    source_customer_id: str
    match_type: Optional[str] = None
    match_score: Optional[Decimal] = None
    matched_at: datetime


class Customer360Response(BaseModel):
    customer: CustomerDetail
    lineage: list[FieldLineageResponse]
    products: dict
    transactions: list[TransactionResponse]
    identity_matches: list[IdentityMatchResponse]


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    address: Optional[str] = None
    changed_by: Optional[str] = "Data Steward"


class CustomerUpdateResponse(BaseModel):
    message: str
    customer: CustomerDetail


class AuditLogResponse(BaseModel):
    audit_id: int
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: Optional[str] = None
    changed_at: datetime
    action: Optional[str] = None


class AuditLogsResponse(BaseModel):
    audit_logs: list[AuditLogResponse]