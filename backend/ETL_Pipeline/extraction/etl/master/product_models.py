"""
ORM models for the revised master product/transaction tables: each product
table links DIRECTLY to master_customer (no customer_product intermediary,
per the revised architecture), and customer_transaction links to exactly
ONE of core_product / credit_card_product / loan_product.
"""

from sqlalchemy import BigInteger, Column, DateTime, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CoreProduct(Base):
    __tablename__ = "core_product"
    __table_args__ = {"schema": "master"}

    core_product_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    master_customer_id = Column(UUID(as_uuid=True), nullable=False)
    source_system = Column(String(50), nullable=False)
    source_customer_id = Column(String(100))
    account_id = Column(String(100))
    account_type = Column(String(30))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class CreditCardProduct(Base):
    __tablename__ = "credit_card_product"
    __table_args__ = {"schema": "master"}

    credit_card_product_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    master_customer_id = Column(UUID(as_uuid=True), nullable=False)
    source_system = Column(String(50), nullable=False)
    source_customer_id = Column(String(100))
    account_id = Column(String(100))
    credit_limit = Column(Numeric(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class LoanProduct(Base):
    __tablename__ = "loan_product"
    __table_args__ = {"schema": "master"}

    loan_product_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    master_customer_id = Column(UUID(as_uuid=True), nullable=False)
    source_system = Column(String(50), nullable=False)
    source_customer_id = Column(String(100))
    loan_amount = Column(Numeric(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class CustomerTransaction(Base):
    __tablename__ = "customer_transaction"
    __table_args__ = {"schema": "master"}

    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    txn_id = Column(String(100), nullable=False)
    account_id = Column(String(100))
    source_system = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2))
    transaction_date = Column(DateTime)
    transaction_type = Column(String(30))
    core_product_id = Column(UUID(as_uuid=True))
    credit_card_product_id = Column(UUID(as_uuid=True))
    loan_product_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
