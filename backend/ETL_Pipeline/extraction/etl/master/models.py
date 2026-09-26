"""
ORM models for the `master` schema tables that the survivorship stage
writes to. Maps to tables that ALREADY EXIST (created by sql/schema.sql)
-- this module never issues CREATE TABLE.

Only the tables survivorship actually needs are modeled here
(master_customer, identity_map, field_lineage, audit_log). The product
tables (core_product, credit_card_product, loan_product,
customer_transaction) belong to the linking stage, not survivorship.
"""

from sqlalchemy import BigInteger, Column, DateTime, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MasterCustomer(Base):
    __tablename__ = "master_customer"
    __table_args__ = {"schema": "master"}

    master_customer_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text)
    email = Column(Text)
    phone = Column(String(50))
    dob = Column(DateTime)  # DATE column
    address = Column(Text)
    quality_score = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class IdentityMap(Base):
    __tablename__ = "identity_map"
    __table_args__ = {"schema": "master"}

    identity_map_id = Column(BigInteger, primary_key=True, autoincrement=True)
    master_customer_id = Column(UUID(as_uuid=True), nullable=False)
    source_system = Column(String(50), nullable=False)
    source_customer_id = Column(String(100), nullable=False)
    match_type = Column(String(20))
    match_score = Column(Numeric(5, 4))
    matched_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class FieldLineage(Base):
    __tablename__ = "field_lineage"
    __table_args__ = {"schema": "master"}

    lineage_id = Column(BigInteger, primary_key=True, autoincrement=True)
    master_customer_id = Column(UUID(as_uuid=True), nullable=False)
    field_name = Column(String(50), nullable=False)
    source_system = Column(String(50))
    source_customer_id = Column(String(100))
    source_value = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "master"}

    audit_id = Column(BigInteger, primary_key=True, autoincrement=True)
    master_customer_id = Column(UUID(as_uuid=True), nullable=False)
    field_name = Column(String(50))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String(100))
    changed_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    action = Column(String(30))
