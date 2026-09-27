create table staging.staging_core_banking (
  staging_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) null,
  source_customer_id character varying(100) not null,
  name text null,
  email text null,
  phone character varying(50) null,
  dob date null,
  address text null,
  processed_at timestamp with time zone not null default now(),
  constraint staging_core_banking_pkey primary key (staging_id),
  constraint fk_staging_core_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;

create table staging.staging_credit_card (
  staging_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) null,
  source_customer_id character varying(100) not null,
  name text null,
  email text null,
  phone character varying(50) null,
  credit_limit numeric(15, 2) null,
  address text null,
  processed_at timestamp with time zone not null default now(),
  constraint staging_credit_card_pkey primary key (staging_id),
  constraint fk_staging_card_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;

create table staging.staging_loan (
  staging_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) null,
  source_customer_id character varying(100) not null,
  name text null,
  phone character varying(50) null,
  loan_amount numeric(15, 2) null,
  address text null,
  processed_at timestamp with time zone not null default now(),
  constraint staging_loan_pkey primary key (staging_id),
  constraint fk_staging_loan_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;

create table staging.staging_transaction (
  staging_id bigserial not null,
  batch_id uuid not null,
  source_file character varying(255) null,
  txn_id character varying(100) not null,
  account_id character varying(100) null,
  amount numeric(15, 2) null,
  transaction_date date null,
  transaction_type character varying(30) null,
  processed_at timestamp with time zone not null default now(),
  source_system character varying(50) null,
  constraint staging_transaction_pkey primary key (staging_id),
  constraint fk_staging_transaction_batch foreign KEY (batch_id) references landing.landing_batch (batch_id)
) TABLESPACE pg_default;
