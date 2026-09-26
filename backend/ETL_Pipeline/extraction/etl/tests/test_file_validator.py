from pathlib import Path

import pytest

from etl.ingestion.file_validator import FileValidationError, validate_source_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_valid_core_banking_file_passes():
    assert validate_source_file(FIXTURES / "core_banking_bad.csv", "core_banking") is True


def test_missing_file_raises():
    with pytest.raises(FileValidationError, match="not found"):
        validate_source_file(FIXTURES / "does_not_exist.csv", "core_banking")


def test_empty_file_raises():
    with pytest.raises(FileValidationError, match="empty"):
        validate_source_file(FIXTURES / "core_banking_empty.csv", "core_banking")


def test_missing_required_column_raises():
    with pytest.raises(FileValidationError, match="missing required column"):
        validate_source_file(FIXTURES / "core_banking_missing_column.csv", "core_banking")
