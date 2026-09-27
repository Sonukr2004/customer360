create table master.master_customer (
  master_customer_id uuid not null default gen_random_uuid (),
  name text null,
  email text null,
  phone character varying(50) null,
  dob date null,
  address text null,
  quality_score numeric(5, 2) null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint master_customer_pkey primary key (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_master_customer_email on master.master_customer using btree (email) TABLESPACE pg_default;

create index IF not exists idx_master_customer_phone on master.master_customer using btree (phone) TABLESPACE pg_default;

create table master.loan_product (
  loan_product_id uuid not null default gen_random_uuid (),
  master_customer_id uuid not null,
  source_system character varying(50) not null default 'SourceC'::character varying,
  source_customer_id character varying(100) null,
  loan_amount numeric(15, 2) null,
  created_at timestamp with time zone not null default now(),
  constraint loan_product_pkey primary key (loan_product_id),
  constraint loan_product_master_customer_id_fkey foreign KEY (master_customer_id) references master.master_customer (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_loan_master_customer on master.loan_product using btree (master_customer_id) TABLESPACE pg_default;

create table master.identity_map (
  identity_map_id bigserial not null,
  master_customer_id uuid not null,
  source_system character varying(50) not null,
  source_customer_id character varying(100) not null,
  match_type character varying(20) null,
  match_score numeric(5, 4) null,
  matched_at timestamp with time zone not null default now(),
  constraint identity_map_pkey primary key (identity_map_id),
  constraint uq_source_identity unique (source_system, source_customer_id),
  constraint identity_map_master_customer_id_fkey foreign KEY (master_customer_id) references master.master_customer (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_identity_master_customer on master.identity_map using btree (master_customer_id) TABLESPACE pg_default;

create index IF not exists idx_identity_source on master.identity_map using btree (source_system, source_customer_id) TABLESPACE pg_default;

create table master.field_lineage (
  lineage_id bigserial not null,
  master_customer_id uuid not null,
  field_name character varying(50) not null,
  source_system character varying(50) null,
  source_customer_id character varying(100) null,
  source_value text null,
  created_at timestamp with time zone not null default now(),
  constraint field_lineage_pkey primary key (lineage_id),
  constraint field_lineage_master_customer_id_fkey foreign KEY (master_customer_id) references master.master_customer (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_lineage_customer on master.field_lineage using btree (master_customer_id) TABLESPACE pg_default;

create table master.customer_transaction (
  transaction_id bigserial not null,
  txn_id character varying(100) not null,
  account_id character varying(100) null,
  source_system character varying(50) not null,
  amount numeric(15, 2) null,
  transaction_date date null,
  transaction_type character varying(30) null,
  core_product_id uuid null,
  credit_card_product_id uuid null,
  created_at timestamp with time zone not null default now(),
  loan_product_id uuid null,
  constraint customer_transaction_pkey primary key (transaction_id),
  constraint uq_source_transaction unique (source_system, txn_id),
  constraint customer_transaction_core_product_id_fkey foreign KEY (core_product_id) references master.core_product (core_product_id),
  constraint customer_transaction_credit_card_product_id_fkey foreign KEY (credit_card_product_id) references master.credit_card_product (credit_card_product_id),
  constraint customer_transaction_loan_product_id_fkey foreign KEY (loan_product_id) references master.loan_product (loan_product_id),
  constraint chk_transaction_product check (
    (
      (
        (
          ((core_product_id is not null))::integer + ((credit_card_product_id is not null))::integer
        ) + ((loan_product_id is not null))::integer
      ) = 1
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_transaction_core on master.customer_transaction using btree (core_product_id) TABLESPACE pg_default;

create index IF not exists idx_transaction_credit_card on master.customer_transaction using btree (credit_card_product_id) TABLESPACE pg_default;

create index IF not exists idx_transaction_date on master.customer_transaction using btree (transaction_date) TABLESPACE pg_default;

create index IF not exists idx_transaction_loan on master.customer_transaction using btree (loan_product_id) TABLESPACE pg_default;

create table master.credit_card_product (
  credit_card_product_id uuid not null default gen_random_uuid (),
  master_customer_id uuid not null,
  source_system character varying(50) not null default 'SourceB'::character varying,
  source_customer_id character varying(100) null,
  account_id character varying(100) null,
  credit_limit numeric(15, 2) null,
  created_at timestamp with time zone not null default now(),
  constraint credit_card_product_pkey primary key (credit_card_product_id),
  constraint uq_credit_card_account unique (source_system, account_id),
  constraint credit_card_product_master_customer_id_fkey foreign KEY (master_customer_id) references master.master_customer (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_credit_card_master_customer on master.credit_card_product using btree (master_customer_id) TABLESPACE pg_default;

create index IF not exists idx_credit_card_account on master.credit_card_product using btree (account_id) TABLESPACE pg_default;

create table master.core_product (
  core_product_id uuid not null default gen_random_uuid (),
  master_customer_id uuid not null,
  source_system character varying(50) not null default 'SourceA'::character varying,
  source_customer_id character varying(100) null,
  account_id character varying(100) null,
  account_type character varying(30) null,
  created_at timestamp with time zone not null default now(),
  constraint core_product_pkey primary key (core_product_id),
  constraint uq_core_account unique (source_system, account_id),
  constraint core_product_master_customer_id_fkey foreign KEY (master_customer_id) references master.master_customer (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_core_master_customer on master.core_product using btree (master_customer_id) TABLESPACE pg_default;

create index IF not exists idx_core_account on master.core_product using btree (account_id) TABLESPACE pg_default;

create table master.audit_log (
  audit_id bigserial not null,
  master_customer_id uuid not null,
  field_name character varying(50) null,
  old_value text null,
  new_value text null,
  changed_by character varying(100) null,
  changed_at timestamp with time zone not null default now(),
  action character varying(30) null,
  constraint audit_log_pkey primary key (audit_id),
  constraint audit_log_master_customer_id_fkey foreign KEY (master_customer_id) references master.master_customer (master_customer_id)
) TABLESPACE pg_default;

create index IF not exists idx_audit_customer on master.audit_log using btree (master_customer_id) TABLESPACE pg_default;
