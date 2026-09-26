"""
ORM models for the `landing` schema tables.

These map to tables that ALREADY EXIST in the database (created by your
schema.sql / Supabase migration) -- this module never issues CREATE TABLE.
Primary keys use server-side defaults (gen_random_uuid() / BIGSERIAL), so
after `session.add(row); session.flush()`, the generated ID is available
on the Python object without any extra query.
"""

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LandingBatch(Base):
    __tablename__ = "landing_batch"
    __table_args__ = {"schema": "landing"}

    batch_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    uploaded_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    uploaded_by = Column(String(100))
    total_files = Column(Integer)
    status = Column(String(20), nullable=False, server_default=text("'UPLOADED'"))


class LandingCoreBanking(Base):
    __tablename__ = "landing_core_banking"
    __table_args__ = {"schema": "landing"}

    landing_core_banking_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("landing.landing_batch.batch_id"), nullable=False)
    source_file = Column(String(255), nullable=False)
    customer_id = Column(String(100))
    name = Column(Text)
    email = Column(Text)
    phone = Column(String(50))
    dob = Column(DateTime)  # DATE column; DateTime works fine for both read/write
    address = Column(Text)


class LandingCreditCard(Base):
    __tablename__ = "landing_credit_card"
    __table_args__ = {"schema": "landing"}

    landing_credit_card_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("landing.landing_batch.batch_id"), nullable=False)
    source_file = Column(String(255), nullable=False)
    cust_ref = Column(String(100))
    name = Column(Text)
    email = Column(Text)
    phone = Column(String(50))
    credit_limit = Column(Numeric(15, 2))
    address = Column(Text)


class LandingLoan(Base):
    __tablename__ = "landing_loan"
    __table_args__ = {"schema": "landing"}

    landing_loan_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("landing.landing_batch.batch_id"), nullable=False)
    source_file = Column(String(255), nullable=False)
    loan_cust_id = Column(String(100))
    name = Column(Text)
    phone = Column(String(50))
    loan_amt = Column(Numeric(15, 2))
    address = Column(Text)


class LandingTransaction(Base):
    __tablename__ = "landing_transaction"
    __table_args__ = {"schema": "landing"}

    landing_transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("landing.landing_batch.batch_id"), nullable=False)
    source_file = Column(String(255), nullable=False)
    txn_id = Column(String(100))
    account_id = Column(String(100))
    amount = Column(Numeric(15, 2))
    transaction_date = Column(DateTime)  # DATE column
    transaction_type = Column(String(30))
