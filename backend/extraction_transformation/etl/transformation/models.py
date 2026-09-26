"""
ORM models for the `staging` and `reference` schema tables. Like
etl/ingestion/models.py, these map to tables that ALREADY EXIST (created by
sql/schema.sql) -- this module never issues CREATE TABLE.
"""

"""
NOTE: batch_id below is a plain UUID column, not a SQLAlchemy ForeignKey --
the real FK constraint to landing.landing_batch already exists in the
database (see sql/schema.sql). Declaring it again here would require
sharing one MetaData/Base with etl.ingestion.models, which isn't necessary
just to insert rows, so we keep the two modules' models independent.
"""

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StagingCoreBanking(Base):
    __tablename__ = "staging_core_banking"
    __table_args__ = {"schema": "staging"}

    staging_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), nullable=False)
    source_file = Column(String(255))
    source_customer_id = Column(String(100), nullable=False)
    name = Column(Text)
    email = Column(Text)
    phone = Column(String(50))
    dob = Column(DateTime)
    address = Column(Text)
    processed_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class StagingCreditCard(Base):
    __tablename__ = "staging_credit_card"
    __table_args__ = {"schema": "staging"}

    staging_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), nullable=False)
    source_file = Column(String(255))
    source_customer_id = Column(String(100), nullable=False)
    name = Column(Text)
    email = Column(Text)
    phone = Column(String(50))
    credit_limit = Column(Numeric(15, 2))
    address = Column(Text)
    processed_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class StagingLoan(Base):
    __tablename__ = "staging_loan"
    __table_args__ = {"schema": "staging"}

    staging_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), nullable=False)
    source_file = Column(String(255))
    source_customer_id = Column(String(100), nullable=False)
    name = Column(Text)
    phone = Column(String(50))
    loan_amount = Column(Numeric(15, 2))
    address = Column(Text)
    processed_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class StagingTransaction(Base):
    __tablename__ = "staging_transaction"
    __table_args__ = {"schema": "staging"}

    staging_id = Column(BigInteger, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True), nullable=False)
    source_file = Column(String(255))
    txn_id = Column(String(100), nullable=False)
    account_id = Column(String(100))
    amount = Column(Numeric(15, 2))
    transaction_date = Column(DateTime)
    transaction_type = Column(String(30))
    processed_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class ReferenceAddress(Base):
    __tablename__ = "reference_address"
    __table_args__ = {"schema": "reference"}

    short_form = Column(String(20), primary_key=True)
    long_form = Column(String(100), nullable=False)


class TrustHierarchy(Base):
    __tablename__ = "trust_hierarchy"
    __table_args__ = {"schema": "reference"}

    field_name = Column(String(50), primary_key=True)
    source_system = Column(String(50), primary_key=True)
    priority = Column(Integer, nullable=False)
