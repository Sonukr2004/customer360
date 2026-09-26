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
│   │   ├── duplicate_checker.py   # flags repeated IDs within one source
│   │   ├── reference_loader.py    # loads reference_data.csv / trust_hierarchy.json
│   │   └── transform.py           # orchestrates the full stage
│   └── tests/                     # 39 tests, run against real Postgres
├── scripts/
│   ├── run_extraction.py
│   └── run_transformation.py
├── requirements.txt
└── .env.example
```

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

Transformation complete:
  core_banking: 1560
  credit_card: 975
  loan: 580
  transaction: 6841
```

## Test

Tests run against a **real Postgres database** (schema-qualified tables and
UUID types don't behave identically on SQLite):

```bash
createdb unibank_pytest
psql unibank_pytest -f sql/schema.sql
export TEST_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/unibank_pytest"
pytest -v
```

39 tests total:
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

## Next stage

Matching (exact email → exact phone → fuzzy name+address) reads from
`staging.*`, resolves duplicate identities into `master.identity_map`, and
survivorship builds `master.master_customer` using `reference.trust_hierarchy`.
