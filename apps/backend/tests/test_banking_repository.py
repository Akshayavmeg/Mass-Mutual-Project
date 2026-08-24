"""Tests for CSVBankingDataRepository (docs/16_Validation_Engine.md S5,
S35) against the real Milestone 1 mock banking dataset, plus the
fail-safe BankingDataUnavailableError behavior required when the data
source cannot be read at all (docs/16 S42).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.repositories.banking_repository import (
    BankingDataUnavailableError,
    CSVBankingDataRepository,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_DATA_DIR = REPO_ROOT / "data" / "mock_banking_data"


@pytest.fixture
def real_repo() -> CSVBankingDataRepository:
    return CSVBankingDataRepository(REAL_DATA_DIR)


def test_get_account_returns_real_record(real_repo):
    account = real_repo.get_account("9000010001")
    assert account is not None
    assert account.account_status in (
        "ACTIVE", "INACTIVE", "CLOSED", "BLOCKED", "FROZEN",
    )
    assert account.routing_number == "121000358"


def test_get_account_returns_none_for_unknown_account(real_repo):
    assert real_repo.get_account("0000000000") is None


def test_get_cheque_issuance_returns_real_record(real_repo):
    issuance = real_repo.get_cheque_issuance("9000010001", "000100")
    assert issuance is not None
    assert issuance.status in ("ISSUED", "PRESENTED", "PAID", "STOPPED", "CANCELLED", "EXPIRED")


def test_get_cheque_issuance_returns_none_for_unknown_pair(real_repo):
    assert real_repo.get_cheque_issuance("9000010001", "999999") is None


def test_find_duplicate_matches_a_real_historical_record(real_repo):
    real_repo._ensure_loaded()
    assert real_repo._processed_history, "expected non-empty processed cheque history"
    sample = next(r for r in real_repo._processed_history if r.cheque_number)
    match = real_repo.find_duplicate(
        sample.account_number, sample.cheque_number, sample.amount, sample.cheque_date,
    )
    assert match is not None
    assert match.cheque_id == sample.cheque_id


def test_find_duplicate_returns_none_when_no_match(real_repo):
    match = real_repo.find_duplicate("9000010001", "000100", 999999.99, "1999-01-01")
    assert match is None


def test_repository_raises_on_missing_data_directory(tmp_path):
    empty_repo = CSVBankingDataRepository(tmp_path)
    with pytest.raises(BankingDataUnavailableError):
        empty_repo.get_account("9000010001")


def test_repository_raises_on_missing_data_directory_for_issuance(tmp_path):
    empty_repo = CSVBankingDataRepository(tmp_path)
    with pytest.raises(BankingDataUnavailableError):
        empty_repo.get_cheque_issuance("9000010001", "000100")


def test_repository_raises_on_missing_data_directory_for_duplicate(tmp_path):
    empty_repo = CSVBankingDataRepository(tmp_path)
    with pytest.raises(BankingDataUnavailableError):
        empty_repo.find_duplicate("9000010001", "000100", 100.0, "2026-08-01")


def test_repository_caches_after_first_load(real_repo):
    real_repo.get_account("9000010001")
    assert real_repo._accounts is not None
    # A second call must not re-read the CSV files -- confirmed indirectly
    # by mutating the cache and observing the mutated value is served.
    real_repo._accounts["9000010001"] = real_repo._accounts["9000010001"].__class__(
        **{**real_repo._accounts["9000010001"].__dict__, "account_status": "TEST_OVERRIDE"},
    )
    assert real_repo.get_account("9000010001").account_status == "TEST_OVERRIDE"
