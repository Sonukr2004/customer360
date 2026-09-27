create table landing.landing_batch (
  batch_id uuid not null default gen_random_uuid (),
  uploaded_at timestamp with time zone not null default now(),
  uploaded_by character varying(100) null,
  total_files integer null,
  status character varying(20) not null default 'UPLOADED'::character varying,
  constraint landing_batch_pkey primary key (batch_id)
) TABLESPACE pg_default;

create table landing.landing_core_banking (
  landing_core_banking_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) not null,
  customer_id character varying(100) null,
  name text null,
  email text null,
  phone character varying(50) null,
  dob date null,
  address text null,
  constraint landing_core_banking_pkey primary key (landing_core_banking_id),
  constraint fk_landing_core_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;

create table landing.landing_credit_card (
  landing_credit_card_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) not null,
  cust_ref character varying(100) null,
  name text null,
  email text null,
  phone character varying(50) null,
  credit_limit numeric(15, 2) null,
  address text null,
  constraint landing_credit_card_pkey primary key (landing_credit_card_id),
  constraint fk_landing_card_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;

create table landing.landing_loan (
  landing_loan_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) not null,
  loan_cust_id character varying(100) null,
  name text null,
  phone character varying(50) null,
  loan_amt numeric(15, 2) null,
  address text null,
  constraint landing_loan_pkey primary key (landing_loan_id),
  constraint fk_landing_loan_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;

create table landing.landing_transaction (
  landing_transaction_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) not null,
  txn_id character varying(100) null,
  account_id character varying(100) null,
  amount numeric(15, 2) null,
  transaction_date date null,
  transaction_type character varying(30) null,
  constraint landing_transaction_pkey primary key (landing_transaction_id),
  constraint fk_landing_transaction_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;
