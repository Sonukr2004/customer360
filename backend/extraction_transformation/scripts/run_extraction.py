#!/usr/bin/env python3
"""
Run the extraction stage against the real dataset in data/, from the
project root:

    python scripts/run_extraction.py

Reads SUPABASE_DB_URL (or DATABASE_URL) and DATA_DIR from .env.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from etl.ingestion.extract import run_extraction  # noqa: E402

if __name__ == "__main__":
    summary = run_extraction()
    print("\nExtraction complete:")
    print(f"  batch_id: {summary['batch_id']}")
    print(f"  status:   {summary['status']}")
    print("  rows loaded per source:")
    for source, count in summary["rows_loaded"].items():
        print(f"    {source}: {count}")
    if summary["errors"]:
        print("  errors:")
        for source, msg in summary["errors"].items():
            print(f"    {source}: {msg}")
