"""Unit tests for each individual Milestone 4 validation rule
(docs/16_Validation_Engine.md S9-S24).

These exercise each validator function directly against crafted
AccountRecord/ChequeIssuanceRecord fixtures so every documented status
value (including ones sparse or absent in the real Milestone 1 dataset,
e.g. EXPIRED/PRESENTED/PAID cheque statuses, INACTIVE/FROZEN account
statuses) is covered, plus the fail-safe NOT_CHECKED behavior for
missing/unavailable data. Full pipeline behavior against real Milestone
1/3 data is covered separately in test_validation_service_milestone4.py.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.repositories.banking_repository import (
    AccountRecord,
    BankingDataUnavailableError,
    ChequeIssuanceRecord,
)
from app.services.validation.validators.account_validator import (
    check_account_exists,
    check_account_status,
)
from app.services.validation.validators.amount_validator import (
    check_amount,
    check_amount_consistency,
)
from app.services.validation.validators.cheque_validator import (
    check_cheque_series,
    check_cheque_status,
)
from app.services.validation.validators.cross_field_validator import check_cross_field
from app.services.validation.validators.date_validator import check_date_window
from app.services.validation.validators.duplicate_validator import check_duplicate
from app.services.validation.validators.payee_validator import check_payee_match
from app.services.validation.validators.required_fields import check_required_fields
from app.services.validation.validators.routing_validator import check_routing_transit
from app.services.validation.models import CheckResult


def _account(**overrides) -> AccountRecord:
    defaults = dict(
        account_number="9000010001",
        customer_id="CUST-0001",
        account_status="ACTIVE",
        account_type="CHECKING",
        balance=1000.0,
        routing_number="121000358",
        bank_code="DEMO001",
        cheque_series_start="000100",
        cheque_series_end="000149",
    )
    defaults.update(overrides)
    return AccountRecord(**defaults)


def _issuance(**overrides) -> ChequeIssuanceRecord:
    defaults = dict(
        cheque_number="000100",
        account_number="9000010001",
        status="ISSUED",
        payee_name="Bluepeak Distributors",
        amount_limit=500000.0,
    )
    defaults.update(overrides)
    return ChequeIssuanceRecord(**defaults)


class _FakeBankingRepo:
    """Minimal BankingDataRepository stand-in that either returns fixed
    values or raises BankingDataUnavailableError, for testing fail-safe
    behavior without touching real CSV files."""

    def __init__(self, *, account=None, issuance=None, duplicate=None, unavailable=False):
        self._account = account
        self._issuance = issuance
        self._duplicate = duplicate
        self._unavailable = unavailable

    def get_account(self, account_number):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._account

    def get_cheque_issuance(self, account_number, cheque_number):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._issuance

    def find_duplicate(self, account_number, cheque_number, amount, cheque_date):
        if self._unavailable:
            raise BankingDataUnavailableError("simulated outage")
        return self._duplicate


# --------------------------------------------------------------------
# REQUIRED_FIELDS
# --------------------------------------------------------------------

def test_required_fields_pass_when_all_present():
    fields = {name: {"value": "x"} for name in
               ("cheque_number", "account_number", "amount", "date", "payee_name")}
    result = check_required_fields(fields)
    assert result.status == "PASS"


def test_required_fields_fail_when_missing():
    fields = {"cheque_number": {"value": "000100"}}
    result = check_required_fields(fields)
    assert result.status == "FAIL"
    assert "account_number" in result.details["missing_fields"]
    assert "payee_name" in result.details["missing_fields"]


# --------------------------------------------------------------------
# ACCOUNT_EXISTS / ACCOUNT_STATUS
# --------------------------------------------------------------------

def test_account_exists_pass():
    repo = _FakeBankingRepo(account=_account())
    result, account = check_account_exists("9000010001", repo)
    assert result.status == "PASS"
    assert account is not None


def test_account_exists_fail_when_unknown():
    repo = _FakeBankingRepo(account=None)
    result, account = check_account_exists("9000099999", repo)
    assert result.status == "FAIL"
    assert account is None


def test_account_exists_not_checked_when_account_number_missing():
    repo = _FakeBankingRepo(account=_account())
    result, account = check_account_exists(None, repo)
    assert result.status == "NOT_CHECKED"
    assert account is None


def test_account_exists_not_checked_when_banking_data_unavailable():
    repo = _FakeBankingRepo(unavailable=True)
    result, account = check_account_exists("9000010001", repo)
    assert result.status == "NOT_CHECKED"
    assert account is None


@pytest.mark.parametrize("status", ["INACTIVE", "CLOSED", "BLOCKED", "FROZEN"])
def test_account_status_fail_for_non_active_statuses(status):
    result = check_account_status(_account(account_status=status))
    assert result.status == "FAIL"
    assert result.details["account_status"] == status


def test_account_status_pass_for_active():
    result = check_account_status(_account(account_status="ACTIVE"))
    assert result.status == "PASS"


def test_account_status_not_checked_when_account_none():
    result = check_account_status(None)
    assert result.status == "NOT_CHECKED"


# --------------------------------------------------------------------
# CHEQUE_SERIES
# --------------------------------------------------------------------

def test_cheque_series_pass_within_range():
    result = check_cheque_series("000125", _account())
    assert result.status == "PASS"


def test_cheque_series_fail_outside_range():
    result = check_cheque_series("000999", _account())
    assert result.status == "FAIL"
    assert result.details["expected_range"] == ["000100", "000149"]


def test_cheque_series_fail_non_numeric():
    result = check_cheque_series("ABCDEF", _account())
    assert result.status == "FAIL"


def test_cheque_series_not_checked_when_account_missing():
    result = check_cheque_series("000125", None)
    assert result.status == "NOT_CHECKED"


def test_cheque_series_not_checked_when_cheque_number_missing():
    result = check_cheque_series(None, _account())
    assert result.status == "NOT_CHECKED"


# --------------------------------------------------------------------
# CHEQUE_STATUS
# --------------------------------------------------------------------

@pytest.mark.parametrize("status", ["PRESENTED", "PAID", "CANCELLED", "EXPIRED"])
def test_cheque_status_fail_for_non_issued_statuses(status):
    repo = _FakeBankingRepo(issuance=_issuance(status=status))
    result, issuance = check_cheque_status("9000010001", "000100", repo)
    assert result.status == "FAIL"
    assert result.severity != "CRITICAL"  # only STOPPED escalates to CRITICAL


def test_cheque_status_pass_for_issued():
    repo = _FakeBankingRepo(issuance=_issuance(status="ISSUED"))
    result, issuance = check_cheque_status("9000010001", "000100", repo)
    assert result.status == "PASS"


def test_cheque_status_stopped_escalates_to_critical_severity():
    repo = _FakeBankingRepo(issuance=_issuance(status="STOPPED"))
    result, issuance = check_cheque_status("9000010001", "000100", repo)
    assert result.status == "FAIL"
    assert result.severity == "CRITICAL"


def test_cheque_status_fail_when_no_issuance_record():
    repo = _FakeBankingRepo(issuance=None)
    result, issuance = check_cheque_status("9000010001", "999999", repo)
    assert result.status == "FAIL"
    assert issuance is None


def test_cheque_status_not_checked_when_missing_inputs():
    repo = _FakeBankingRepo(issuance=_issuance())
    result, issuance = check_cheque_status(None, "000100", repo)
    assert result.status == "NOT_CHECKED"


def test_cheque_status_not_checked_when_banking_data_unavailable():
    repo = _FakeBankingRepo(unavailable=True)
    result, issuance = check_cheque_status("9000010001", "000100", repo)
    assert result.status == "NOT_CHECKED"


# --------------------------------------------------------------------
# DATE_WINDOW
# --------------------------------------------------------------------

def test_date_window_pass_for_recent_date():
    result = check_date_window("2026-08-01", date(2026, 8, 23))
    assert result.status == "PASS"


def test_date_window_fail_for_future_date():
    result = check_date_window("2026-09-28", date(2026, 8, 23))
    assert result.status == "FAIL"
    assert "future-dated" in result.message


def test_date_window_fail_for_stale_date():
    result = check_date_window("2025-01-01", date(2026, 8, 23))
    assert result.status == "FAIL"
    assert "days old" in result.message


def test_date_window_fail_for_invalid_format():
    result = check_date_window("not-a-date", date(2026, 8, 23))
    assert result.status == "FAIL"


def test_date_window_not_checked_when_missing():
    result = check_date_window(None, date(2026, 8, 23))
    assert result.status == "NOT_CHECKED"


def test_date_window_allows_future_dated_when_configured(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "allow_future_dated_cheques", True)
    result = check_date_window("2026-09-28", date(2026, 8, 23))
    assert result.status == "PASS"


# --------------------------------------------------------------------
# PAYEE_MATCH
# --------------------------------------------------------------------

def test_payee_match_pass_exact():
    result = check_payee_match("Bluepeak Distributors", _issuance(payee_name="Bluepeak Distributors"))
    assert result.status == "PASS"


def test_payee_match_pass_case_and_whitespace_insensitive():
    result = check_payee_match("  bluepeak   distributors  ", _issuance(payee_name="Bluepeak Distributors"))
    assert result.status == "PASS"


def test_payee_match_fail_mismatch():
    result = check_payee_match("Grace Rossi", _issuance(payee_name="Diego Okafor"))
    assert result.status == "FAIL"


def test_payee_match_not_checked_when_payee_missing():
    result = check_payee_match(None, _issuance())
    assert result.status == "NOT_CHECKED"


def test_payee_match_not_checked_when_issuance_missing():
    result = check_payee_match("Grace Rossi", None)
    assert result.status == "NOT_CHECKED"


# --------------------------------------------------------------------
# ROUTING_TRANSIT
# --------------------------------------------------------------------

def test_routing_transit_pass_match():
    result = check_routing_transit("121000358", _account(routing_number="121000358"))
    assert result.status == "PASS"


def test_routing_transit_fail_mismatch():
    result = check_routing_transit("999999999", _account(routing_number="121000358"))
    assert result.status == "FAIL"


def test_routing_transit_not_checked_when_value_missing():
    result = check_routing_transit(None, _account())
    assert result.status == "NOT_CHECKED"


def test_routing_transit_not_checked_when_account_missing():
    result = check_routing_transit("121000358", None)
    assert result.status == "NOT_CHECKED"


# --------------------------------------------------------------------
# AMOUNT / AMOUNT_CONSISTENCY
# --------------------------------------------------------------------

def test_amount_pass_for_valid_value():
    result = check_amount(1000.0)
    assert result.status == "PASS"


def test_amount_fail_for_zero():
    result = check_amount(0.0)
    assert result.status == "FAIL"


def test_amount_fail_for_negative():
    result = check_amount(-50.0)
    assert result.status == "FAIL"


def test_amount_fail_for_over_max(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "max_permitted_cheque_amount", 500.0)
    result = check_amount(1000.0)
    assert result.status == "FAIL"


def test_amount_not_checked_when_missing():
    result = check_amount(None)
    assert result.status == "NOT_CHECKED"


def test_amount_consistency_pass_when_matching():
    result = check_amount_consistency(17334.23, "Seventeen Thousand Three Hundred Thirty Four and 23/100 Only")
    assert result.status == "PASS"


def test_amount_consistency_fail_when_mismatched():
    result = check_amount_consistency(8650.21, "Two Thousand Three Hundred Sixty and 18/100 Only")
    assert result.status == "FAIL"


def test_amount_consistency_not_checked_when_words_missing():
    result = check_amount_consistency(100.0, None)
    assert result.status == "NOT_CHECKED"


def test_amount_consistency_warning_when_words_unparseable():
    result = check_amount_consistency(100.0, "###unreadable###")
    assert result.status == "WARNING"


# --------------------------------------------------------------------
# DUPLICATE_CHECK
# --------------------------------------------------------------------

def test_duplicate_check_pass_when_no_match():
    repo = _FakeBankingRepo(duplicate=None)
    result = check_duplicate(
        cheque_id="CHK-1", account_number="9000010001", cheque_number="000100",
        amount=100.0, date_value="2026-08-01", banking_repo=repo, live_candidates=[],
    )
    assert result.status == "PASS"


def test_duplicate_check_fail_on_historical_match():
    from app.repositories.banking_repository import DuplicateMatch
    match = DuplicateMatch(
        cheque_id="PROC-000001", account_number="9000010001", cheque_number="000100",
        payee_name="X", amount=100.0, cheque_date="2026-08-01",
    )
    repo = _FakeBankingRepo(duplicate=match)
    result = check_duplicate(
        cheque_id="CHK-1", account_number="9000010001", cheque_number="000100",
        amount=100.0, date_value="2026-08-01", banking_repo=repo, live_candidates=[],
    )
    assert result.status == "FAIL"
    assert result.details["matched_cheque_id"] == "PROC-000001"


def test_duplicate_check_fail_on_live_session_match():
    repo = _FakeBankingRepo(duplicate=None)
    live_candidates = [{
        "cheque_id": "CHK-OTHER", "account_number": "9000010001", "cheque_number": "000100",
        "amount": 100.0, "cheque_date": "2026-08-01",
    }]
    result = check_duplicate(
        cheque_id="CHK-1", account_number="9000010001", cheque_number="000100",
        amount=100.0, date_value="2026-08-01", banking_repo=repo, live_candidates=live_candidates,
    )
    assert result.status == "FAIL"
    assert result.details["matched_cheque_id"] == "CHK-OTHER"


def test_duplicate_check_ignores_self_in_live_candidates():
    repo = _FakeBankingRepo(duplicate=None)
    live_candidates = [{
        "cheque_id": "CHK-1", "account_number": "9000010001", "cheque_number": "000100",
        "amount": 100.0, "cheque_date": "2026-08-01",
    }]
    result = check_duplicate(
        cheque_id="CHK-1", account_number="9000010001", cheque_number="000100",
        amount=100.0, date_value="2026-08-01", banking_repo=repo, live_candidates=live_candidates,
    )
    assert result.status == "PASS"


def test_duplicate_check_not_checked_when_fields_missing():
    repo = _FakeBankingRepo(duplicate=None)
    result = check_duplicate(
        cheque_id="CHK-1", account_number=None, cheque_number="000100",
        amount=100.0, date_value="2026-08-01", banking_repo=repo, live_candidates=[],
    )
    assert result.status == "NOT_CHECKED"


def test_duplicate_check_not_checked_when_banking_data_unavailable():
    repo = _FakeBankingRepo(unavailable=True)
    result = check_duplicate(
        cheque_id="CHK-1", account_number="9000010001", cheque_number="000100",
        amount=100.0, date_value="2026-08-01", banking_repo=repo, live_candidates=[],
    )
    assert result.status == "NOT_CHECKED"


# --------------------------------------------------------------------
# CROSS_FIELD
# --------------------------------------------------------------------

def test_cross_field_pass_when_both_ok():
    checks = {
        "ACCOUNT_STATUS": CheckResult("ACCOUNT_STATUS", "PASS", "INFO", "ok"),
        "CHEQUE_STATUS": CheckResult("CHEQUE_STATUS", "PASS", "INFO", "ok"),
    }
    result = check_cross_field(checks)
    assert result.status == "PASS"


def test_cross_field_warning_when_both_fail():
    checks = {
        "ACCOUNT_STATUS": CheckResult("ACCOUNT_STATUS", "FAIL", "HIGH", "closed"),
        "CHEQUE_STATUS": CheckResult("CHEQUE_STATUS", "FAIL", "HIGH", "stopped"),
    }
    result = check_cross_field(checks)
    assert result.status == "WARNING"


def test_cross_field_pass_when_only_one_fails():
    checks = {
        "ACCOUNT_STATUS": CheckResult("ACCOUNT_STATUS", "FAIL", "HIGH", "closed"),
        "CHEQUE_STATUS": CheckResult("CHEQUE_STATUS", "PASS", "INFO", "ok"),
    }
    result = check_cross_field(checks)
    assert result.status == "PASS"


def test_cross_field_not_checked_when_inputs_missing():
    result = check_cross_field({})
    assert result.status == "NOT_CHECKED"
