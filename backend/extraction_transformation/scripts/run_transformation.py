#!/usr/bin/env python3
"""
Run the transformation stage (landing.* -> staging.*, plus loading
reference.* config) against the real dataset, from the project root:

    python scripts/run_transformation.py

Run scripts/run_extraction.py first -- transformation processes only the
MOST RECENT batch currently in landing.landing_batch.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from etl.transformation.transform import run_transformation  # noqa: E402

if __name__ == "__main__":
    summary = run_transformation()
    duplicates = summary.pop("duplicates_found")
    batch_id = summary.pop("batch_id")

    print(f"\nTransformation complete (batch {batch_id}):")
    for source, count in summary.items():
        print(f"  {source}: {count}")

    any_duplicates = any(duplicates.values())
    if any_duplicates:
        print("\nDuplicate IDs detected within this batch (needs review):")
        for source, dupes in duplicates.items():
            for dup_id, occurrences in dupes.items():
                print(f"  {source}: {dup_id!r} appears {occurrences} times")
    else:
        print("\nNo duplicate IDs detected within this batch.")
