"""Config for the extraction module: where the source files live."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))

CORE_BANKING_FILE = DATA_DIR / "core_banking.csv"
CREDIT_CARD_FILE = DATA_DIR / "credit_card.csv"
# Prefer the CSV if present; loader.py also accepts the .jsonl transparently
# if you point LOAN_FILE at it instead (same data, alternate format).
LOAN_FILE = DATA_DIR / "loan_system.csv"
TRANSACTION_FILE = DATA_DIR / "transaction_data.csv"
