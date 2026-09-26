# UniBank Customer 360 — Extraction + Transformation (ETL)

Two pipeline stages, both verified against a real PostgreSQL 16 instance:

1. **Extraction** — reads the raw source files and lands them into the
   `landing` schema, untouched (just correctly typed).
2. **Transformation** — reads `landing.*`, cleans and standardizes it
   (Proper Case names, lowercased emails, formatted phones, reference-data
   address standardization), checks for duplicate IDs within a single
   source, and writes the result to `staging.*`. Also loads
   `reference_data.csv` / `trust_hierarchy.json` into `reference.*`.

Matching, survivorship, and the Golden Record (`master.*`) are the next
stages, not yet built.

**Verified against real data, not just fixtures**: ran the full dataset
through both stages — 1,560 + 975 + 580 + 6,841 = 9,956 rows landed, then
staged with real address standardization (`"383 Stone Ct., Suite 19,
Vasquezburgh"` → `"383 Stone Court Suite 19 Vasquezburgh"`), zero mangled
tokens (checked specifically that no "St." rule ever corrupts a real
"Street").

## Pipeline

```
CSV/JSONL files          reference_data.csv
      │                  trust_hierarchy.json
      ▼                        │
  [extraction]                 ▼
      │                  [reference_loader]
      ▼                        │
  landing.landing_*            ▼
      │                  reference.reference_address
      ▼                  reference.trust_hierarchy
  [transformation] ◄───────────┘
      │  (name/email/phone/address standardizers)
      ▼
  staging.staging_*
```

## Project structure

```
project/
├── data/                          # dataset (CSV/JSONL/JSON)
├── sql/
│   └── schema.sql                 # landing/staging/reference/master DDL
├── etl/
│   ├── ingestion/                 # STAGE 1: extraction
│   │   ├── config.py
│   │   ├── db.py                  # shared Postgres/Supabase connection
│   │   ├── models.py              # ORM models for landing.*
│   │   ├── file_validator.py
│   │   ├── batch_manager.py
│   │   ├── loader.py
│   │   └── extract.py
│   ├── transformation/            # STAGE 2: cleaning + standardization
│   │   ├── models.py              # ORM models for staging.* / reference.*
│   │   ├── cleaner.py             # shared null-handling + trim helpers
│   │   ├── name_standardizer.py
│   │   ├── email_standardizer.py
│   │   ├── phone_standardizer.py
│   │   ├── address_standardizer.py  # reads reference.reference_address
│   │   ├── duplicate_checker.py   # flags repeated IDs within one batch
│   │   ├── reference_loader.py    # loads reference_data.csv / trust_hierarchy.json
│   │   └── transform.py           # orchestrates the full stage
│   ├── matching/                   # STAGE 3: identity resolution
│   │   ├── exact_match.py         # exact email, exact phone (cross-source only)
│   │   ├── fuzzy_match.py         # fuzzy name+address (blocked, allows same-source)
│   │   └── identity_resolver.py   # Union-Find orchestration, builds clusters
│   ├── survivorship/               # STAGE 4: field-level Golden Record resolution
│   │   ├── hierarchy_loader.py    # reads reference.trust_hierarchy back into a lookup
│   │   └── survivor_engine.py     # pure logic: resolve_field, build_golden_fields
│   ├── master/                     # persists resolved clusters to master.*
│   │   ├── models.py              # ORM models for master_customer/identity_map/field_lineage/audit_log
│   │   ├── customer_loader.py     # persist_golden_customer() -- also triggers product linking
│   │   ├── product_models.py      # ORM models for core/credit_card/loan_product + customer_transaction
│   │   ├── product_loader.py      # link_products() -- one row per source record in a cluster
│   │   ├── transaction_loader.py  # link_transactions() -- resolves Account_ID to its product
│   │   └── override_service.py    # override_field() -- manual edits, writes audit_log
│   └── tests/                     # 86 tests, run against real Postgres
├── scripts/
│   ├── run_extraction.py
│   ├── run_transformation.py
│   ├── run_matching_and_survivorship.py   # matching -> survivorship -> products -> transactions
│   ├── demo_manual_override.py            # demonstrates override_field() + audit_log against real data
│   ├── evaluate_matching_against_ground_truth.py
│   └── validate_survivorship_against_ground_truth.py
├── requirements.txt
└── .env.example
```

**Master schema note:** `core_product` / `credit_card_product` / `loan_product`
link DIRECTLY to `master_customer_id` (no `customer_product` intermediary --
that table was removed in a later revision). `customer_transaction` links to
EXACTLY ONE of `core_product_id` / `credit_card_product_id` / `loan_product_id`
(a 3-way `CHECK` constraint enforces this) -- extended from the original
2-way core/credit-card-only design specifically because the real dataset's
`transaction_data.csv` has 1,273 loan-linked transactions that the 2-way
version couldn't represent at all.


**Matching is now built and wired to survivorship.** `run_matching_and_survivorship.py`
reads `staging.*`, resolves identities, and persists Golden Customers to
`master.*` in one run. `validate_survivorship_against_ground_truth.py` is
kept as-is (still validates survivorship in isolation using ground truth
as a stand-in cluster source); `evaluate_matching_against_ground_truth.py`
is the new, real test of matching itself.

## Setup

**1. Apply the schema to your Supabase project** (SQL Editor, or `psql`):
```bash
psql "<your Supabase connection string>" -f sql/schema.sql
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```
See the comment at the top of `requirements.txt` if `psycopg2-binary` fails
to install on Windows (common — needs `pg_config` to build from source if
no wheel matches your Python version). Use `psycopg[binary]` instead and
change your connection string's scheme to `postgresql+psycopg://`.

**3. Configure your connection:**
```bash
cp .env.example .env
```
Edit `.env` with your real Supabase connection string. If your network
can't resolve the direct `db.<ref>.supabase.co` host (common — that host
needs IPv6), use the **Session pooler** string from Supabase's Connect
panel instead:
```
SUPABASE_DB_URL=postgresql+psycopg2://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

## Run

```bash
python scripts/run_extraction.py
python scripts/run_transformation.py
python scripts/run_matching_and_survivorship.py
```

Expected output:
```
Extraction complete:
  batch_id: <uuid>
  status:   LOADED
  rows loaded per source:
    core_banking: 1560
    credit_card: 975
    loan: 580
    transaction: 6841

Transformation complete (batch <uuid>):
  core_banking: 1560
  credit_card: 975
  loan: 580
  transaction: 6841

No duplicate IDs detected within this batch.

Matching + survivorship complete:
  source records processed: 3115
  golden customers created: 1771
  match evidence breakdown (per source record):
    exact_email: 595
    exact_phone: 1752
    fuzzy_name_address: 31
    unmatched: 737

Transaction linking complete:
  linked:     6841
  unresolved: 0
```

**Verified against the real dataset**: 1,771 Golden Customers from 3,115
source records, **all 6,841 transactions linked with zero unresolved**
(3,460 core + 2,108 credit card + 1,273 loan — matches the raw
`transaction_data.csv` breakdown exactly), and **100% accuracy** on all 42
evaluable rows in `ground_truth_mapping.csv`
(`scripts/evaluate_matching_against_ground_truth.py`) -- every
ground-truth-verified customer's known source IDs landed under
the exact same `master_customer_id`, no partial or missed merges.

## Test

Tests run against a **real Postgres database** (schema-qualified tables and
UUID types don't behave identically on SQLite):

```bash
createdb unibank_pytest
psql unibank_pytest -f sql/schema.sql
export TEST_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/unibank_pytest"
pytest -v
```

86 tests total:
- **Extraction (16)**: file validation, date/decimal parsing edge cases,
  full extraction integration (bad rows land as `NULL` rather than
  crashing, JSONL loan data loads correctly, landing data really is raw).
- **Transformation (23)**: name/email/phone/address standardizer unit
  tests (including the "don't mangle 'Street' via the 'St' rule" edge
  case), reference/trust-hierarchy loading (including upsert-safety on
  rerun, and parsing `trust_hierarchy.json`'s leading explanatory text),
  duplicate-ID detection (a repeated Customer_ID within one source is
  reported without blocking the rest of the pipeline or dropping data),
  and a full extraction→transformation integration test proving staging
  is correctly cleaned, transactions pass through unchanged, and
  re-running transformation is idempotent (truncate + rebuild, not
  append).
- **Matching (17)**: exact email/phone (cross-source only, ignores nulls,
  doesn't touch same-source pairs), fuzzy name+address (blocking, both
  fields must independently clear the threshold, allowed within the same
  source for real intra-source duplicates, skips pairs already linked by
  an earlier rule), and identity-resolution integration tests proving the
  actual cluster shape and per-record match provenance.
- **Survivorship (8)**: field-specific winner resolution (different
  sources can win different fields in the same cluster), null candidates
  never win regardless of source priority, unranked sources degrade
  gracefully instead of crashing.
- **Master persistence (4)** + **transaction-loader unit (3)** +
  **full pipeline integration (9)**: proves extraction → transformation →
  matching → survivorship → product linking → transaction linking →
  persisted `master.*` end to end, including that `field_lineage` correctly
  attributes each winning field to its actual source, that each cluster's
  source records produce the right number of `core_product` /
  `credit_card_product` / `loan_product` rows, and that two transactions
  from different raw source IDs in the same cluster resolve to the exact
  same Golden Customer -- the specific scenario the PS calls out for
  integration testing.
- **Manual override (6)**: `override_field()` updates `master_customer`,
  writes an `audit_log` row (old value, new value, who, when), and updates
  `field_lineage` to show `DataSteward` as the field's new source --
  including that an unknown field or unknown customer raises cleanly
  rather than silently no-op'ing, and that repeated overrides on the same
  field each get their own audit row rather than overwriting the last one.


## Design notes

- **Staging is a full-refresh derived layer.** Since `staging.*` has no
  `landing_id` back-reference in the schema (by design), transformation
  truncates and rebuilds staging from whatever's currently in landing on
  every run, rather than trying to track "already processed" rows. Landing
  is always the source of truth.
- **Phone normalization keeps the country code if the source gave one, but
  never adds or strips it** — it only removes formatting characters
  (spaces, dashes, `+`). A plain 10-digit number stays 10 digits.
- **Email normalization is trim + lowercase only** — no format validation
  or rejection at this stage; that's a judgment call left to matching, not
  cleaning.
- **Address standardization matches whole tokens only**, so a real
  "Street" is never partially matched and corrupted just because "St" is
  a known abbreviation — verified against the real dataset with zero
  mangled tokens.
- **`reference.*` is treated as config, not batch data** — loaded via
  upsert every run, safe to re-run any number of times.
- **Duplicate checks catch a different problem than matching does.**
  `duplicate_checker.py` flags the *same* ID appearing twice within *one*
  source (e.g. `C0001` showing up twice in `core_banking.csv` — a
  re-issued ID or export bug). It does **not** catch the same real person
  appearing under *different* IDs across sources (e.g. Core Banking's
  `C0001` and Credit Card's `CC_100` both being John Doe) — that's
  cross-source identity resolution, which is the matching stage's job.
  Running this against the real dataset finds zero duplicates (the data
  is clean on this front), which is a different, correct result from
  `ground_truth_mapping.csv`'s `Core_Banking_Duplicate_IDs` column, which
  tracks the cross-source case, not this one.
- **Survivorship is field-specific, not source-specific** — there is no
  single "most trusted source." In the same cluster, SourceA can win
  Phone while SourceB wins Email, per `reference.trust_hierarchy`. A
  candidate with a null value is never eligible to win a field, regardless
  of its source's priority — a highly-trusted source that didn't provide
  a field must not blank it out when another source did.
- **Survivorship validated against real data**: using
  `ground_truth_mapping.csv`'s independently-verified customer groupings
  as clusters (a stand-in for matching, not yet built), the engine's
  chosen winner for Name, DOB, and Phone matches the verified "true" value
  for **100% of the 60 checkable ground-truth customers**
  (`scripts/validate_survivorship_against_ground_truth.py`).

## Verify the audit trail yourself

Run `scripts/demo_manual_override.py` against real data (after
`run_matching_and_survivorship.py` has populated `master.master_customer`)
to see `override_field()` work end to end -- picks a real customer,
changes their phone, and prints the before/after plus the resulting
`audit_log` and `field_lineage` rows:
```bash
python scripts/demo_manual_override.py
```

## Next stage

The Customer 360 API layer: reads from `master.*` (joining
`master_customer` + `field_lineage` for the Source Trace, `core_product` /
`credit_card_product` / `loan_product` for the product portfolio, and
`customer_transaction` for the transaction timeline) to serve search and
the detail view, and calls `override_service.override_field()` (already
built and tested) behind the manual-edit endpoint.
