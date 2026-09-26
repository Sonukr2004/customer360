CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS master;

CREATE TABLE landing.landing_batch (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploaded_by VARCHAR(100),
    total_files INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'UPLOADED'
);

CREATE TABLE landing.landing_core_banking (
    landing_core_banking_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    customer_id VARCHAR(100),
    name TEXT,
    email TEXT,
    phone VARCHAR(50),
    dob DATE,
    address TEXT,
    CONSTRAINT fk_landing_core_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE landing.landing_credit_card (
    landing_credit_card_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    cust_ref VARCHAR(100),
    name TEXT,
    email TEXT,
    phone VARCHAR(50),
    credit_limit NUMERIC(15,2),
    address TEXT,
    CONSTRAINT fk_landing_card_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE landing.landing_loan (
    landing_loan_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    loan_cust_id VARCHAR(100),
    name TEXT,
    phone VARCHAR(50),
    loan_amt NUMERIC(15,2),
    address TEXT,
    CONSTRAINT fk_landing_loan_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE landing.landing_transaction (
    landing_transaction_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    txn_id VARCHAR(100),
    account_id VARCHAR(100),
    amount NUMERIC(15,2),
    transaction_date DATE,
    transaction_type VARCHAR(30),
    CONSTRAINT fk_landing_transaction_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE staging.staging_core_banking (
    staging_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255),
    source_customer_id VARCHAR(100) NOT NULL,
    name TEXT,
    email TEXT,
    phone VARCHAR(50),
    dob DATE,
    address TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_staging_core_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE staging.staging_credit_card (
    staging_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255),
    source_customer_id VARCHAR(100) NOT NULL,
    name TEXT,
    email TEXT,
    phone VARCHAR(50),
    credit_limit NUMERIC(15,2),
    address TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_staging_card_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE staging.staging_loan (
    staging_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255),
    source_customer_id VARCHAR(100) NOT NULL,
    name TEXT,
    phone VARCHAR(50),
    loan_amount NUMERIC(15,2),
    address TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_staging_loan_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE staging.staging_transaction (
    staging_id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    source_file VARCHAR(255),
    txn_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100),
    amount NUMERIC(15,2),
    transaction_date DATE,
    transaction_type VARCHAR(30),
    source_system VARCHAR(50),
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_staging_transaction_batch FOREIGN KEY (batch_id) REFERENCES landing.landing_batch(batch_id)
);

CREATE TABLE reference.reference_address (
    short_form VARCHAR(20) PRIMARY KEY,
    long_form VARCHAR(100) NOT NULL
);

CREATE TABLE reference.trust_hierarchy (
    field_name VARCHAR(50) NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    priority INTEGER NOT NULL,
    PRIMARY KEY (field_name, source_system)
);

CREATE TABLE master.master_customer (
    master_customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    email TEXT,
    phone VARCHAR(50),
    dob DATE,
    address TEXT,
    quality_score NUMERIC(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE master.identity_map (
    identity_map_id BIGSERIAL PRIMARY KEY,
    master_customer_id UUID NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    source_customer_id VARCHAR(100) NOT NULL,
    match_type VARCHAR(20),
    match_score NUMERIC(5,4),
    matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_identity_master FOREIGN KEY (master_customer_id) REFERENCES master.master_customer(master_customer_id),
    CONSTRAINT uq_source_identity UNIQUE (source_system, source_customer_id)
);

CREATE TABLE master.core_product (
    core_product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_customer_id UUID NOT NULL,
    source_system VARCHAR(50) NOT NULL DEFAULT 'SourceA',
    source_customer_id VARCHAR(100),
    account_id VARCHAR(100),
    account_type VARCHAR(30),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_core_customer FOREIGN KEY (master_customer_id) REFERENCES master.master_customer(master_customer_id),
    CONSTRAINT uq_core_account UNIQUE (source_system, account_id)
);

CREATE TABLE master.credit_card_product (
    credit_card_product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_customer_id UUID NOT NULL,
    source_system VARCHAR(50) NOT NULL DEFAULT 'SourceB',
    source_customer_id VARCHAR(100),
    account_id VARCHAR(100),
    credit_limit NUMERIC(15,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_credit_card_customer FOREIGN KEY (master_customer_id) REFERENCES master.master_customer(master_customer_id),
    CONSTRAINT uq_credit_card_account UNIQUE (source_system, account_id)
);

CREATE TABLE master.loan_product (
    loan_product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_customer_id UUID NOT NULL,
    source_system VARCHAR(50) NOT NULL DEFAULT 'SourceC',
    source_customer_id VARCHAR(100),
    loan_amount NUMERIC(15,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_loan_customer FOREIGN KEY (master_customer_id) REFERENCES master.master_customer(master_customer_id)
);

-- A transaction belongs to EXACTLY ONE of core_product / credit_card_product
-- / loan_product (not master_customer_id directly) -- reached the Golden
-- Customer via whichever product it's linked to.
CREATE TABLE master.customer_transaction (
    transaction_id BIGSERIAL PRIMARY KEY,
    txn_id VARCHAR(100) NOT NULL,
    account_id VARCHAR(100),
    source_system VARCHAR(50) NOT NULL,
    amount NUMERIC(15,2),
    transaction_date DATE,
    transaction_type VARCHAR(30),
    core_product_id UUID,
    credit_card_product_id UUID,
    loan_product_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_transaction_core FOREIGN KEY (core_product_id) REFERENCES master.core_product(core_product_id),
    CONSTRAINT fk_transaction_credit_card FOREIGN KEY (credit_card_product_id) REFERENCES master.credit_card_product(credit_card_product_id),
    CONSTRAINT fk_transaction_loan FOREIGN KEY (loan_product_id) REFERENCES master.loan_product(loan_product_id),
    CONSTRAINT uq_source_transaction UNIQUE (source_system, txn_id),
    CONSTRAINT chk_transaction_product CHECK (
        (core_product_id IS NOT NULL)::int +
        (credit_card_product_id IS NOT NULL)::int +
        (loan_product_id IS NOT NULL)::int = 1
    )
);

CREATE TABLE master.field_lineage (
    lineage_id BIGSERIAL PRIMARY KEY,
    master_customer_id UUID NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    source_system VARCHAR(50),
    source_customer_id VARCHAR(100),
    source_value TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_lineage_master FOREIGN KEY (master_customer_id) REFERENCES master.master_customer(master_customer_id)
);

CREATE TABLE master.audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    master_customer_id UUID NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action VARCHAR(30),
    CONSTRAINT fk_audit_master FOREIGN KEY (master_customer_id) REFERENCES master.master_customer(master_customer_id)
);
