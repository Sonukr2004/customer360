# UniBank Customer 360 — Extraction (Ingestion) Module

Reads the raw source files and lands them into the `landing` schema exactly
as they're defined in `sql/schema.sql` — no cleaning, no matching, just
validated raw data with correct column TYPES, tagged by batch and source
file. This is the first stage of the pipeline; cleaning/standardization is
the next stage.

**Verified against a real PostgreSQL 16 instance** (schema-qualified tables,
UUID PKs with `gen_random_uuid()`, `NUMERIC`/`DATE` columns) running your
exact `sql/schema.sql` — not just SQLite. Ran the full real dataset through
it: 1,560 + 975 + 580 + 6,841 = **9,956 rows landed correctly** with real
`date`/`numeric` types, in under a second.

## What "extraction" means here

```
CSV/JSONL files  →  validate  →  create batch  →  land into Postgres
   (data/)                        (landing.landing_batch)   (landing.landing_*)
```

- **Validates** each file exists, is non-empty, and has the required
  columns *before* touching the database.
- **Creates one `landing_batch` row per run** — every row loaded in this
  run shares that `batch_id`, so you can always trace "which upload
  produced this data."
- **Lands raw values untouched** (no trimming, no Proper Case, no address
  standardization — that's the next stage, cleaning). The only conversion
  done here is casting strings into the column types your schema already
  declares (`DATE`, `NUMERIC`), since those columns aren't `TEXT`.
- **A row with an unparseable date/number still lands** (that one field
  becomes `NULL`, logged as a warning) rather than being dropped or
  crashing the whole file — matches the "graceful handling of invalid
  inputs" expectation.
- **One bad file doesn't sink the batch.** If `credit_card.csv` fails
  validation, `core_banking.csv` and the others still load; the batch
  ends up `PARTIALLY_LOADED` with the specific error recorded, not `FAILED`
  outright.
- Loan data loads from **either `.csv` or `.jsonl`** — same loader function
  handles both, since the PS provides both formats for that source.

## Project structure

```
project/
├── data/                          # your dataset (CSV/JSONL/JSON)
├── sql/
│   └── schema.sql                 # your exact landing/staging/reference/master DDL
├── etl/
│   ├── ingestion/
│   │   ├── config.py              # file paths (env-driven)
│   │   ├── db.py                  # Postgres/Supabase connection
│   │   ├── models.py              # ORM models for the landing tables
│   │   ├── file_validator.py      # existence/empty/required-column checks
│   │   ├── batch_manager.py       # landing_batch create/status
│   │   ├── loader.py              # reads files, inserts into landing.*
│   │   └── extract.py             # orchestrates the full run
│   └── tests/                     # 16 tests, run against real Postgres
├── scripts/
│   └── run_extraction.py
├── requirements.txt
└── .env.example
```

## Setup

**1. Apply the schema to your Supabase project** (SQL Editor in the
Supabase dashboard, or `psql`):
```bash
psql "<your Supabase connection string>" -f sql/schema.sql
```
(It's the exact DDL you provided — schemas, tables, indexes, all of it.
Includes `CREATE EXTENSION IF NOT EXISTS pgcrypto` for `gen_random_uuid()`,
which Supabase projects have available by default.)

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure your connection:**
```bash
cp .env.example .env
```
Edit `.env` with your real Supabase connection string:
```
SUPABASE_DB_URL=postgresql+psycopg2://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
```
(Supabase gives you a `postgres://...` URI — just change the scheme to
`postgresql+psycopg2://` and use it as-is.)

## Run

```bash
python scripts/run_extraction.py
```

Expected output (against the real dataset):
```
Extraction complete:
  batch_id: <uuid>
  status:   LOADED
  rows loaded per source:
    core_banking: 1560
    credit_card: 975
    loan: 580
    transaction: 6841
```

## Test

Tests run against a **real Postgres database** (schema-qualified tables and
UUID types don't behave identically on SQLite), so point `TEST_DATABASE_URL`
at any throwaway Postgres database with `sql/schema.sql` applied:

```bash
createdb unibank_pytest
psql unibank_pytest -f sql/schema.sql
export TEST_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/unibank_pytest"
pytest -v
```
16 tests: file validation (missing file, empty file, missing required
column), date/decimal parsing edge cases, and a full extraction integration
test (including that a bad row lands with `NULL` rather than crashing, that
loan data loads correctly from JSONL, and that landing data really is raw —
not cleaned — since that's the next stage's job).

## Next stage

Cleaning/standardization reads from `landing.*`, writes to `staging.*`
(same shape, but trimmed/Proper-Cased/address-standardized) — that's a
separate module reading these exact landing tables as its input.
