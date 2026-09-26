from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CustomerResponse(BaseModel):
    master_customer_id: UUID
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    dob: date | None = None
    address: str | None = None
    quality_score: Decimal | None = None


class CustomersResponse(BaseModel):
    customers: list[CustomerResponse]