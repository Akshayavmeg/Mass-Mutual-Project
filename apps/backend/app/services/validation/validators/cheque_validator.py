"""CHEQUE_SERIES / CHEQUE_STATUS checks (docs/16_Validation_Engine.md
S12-S13)."""

from __future__ import annotations

from app.core.config import settings
from app.repositories.banking_repository import (
    AccountRecord,
    BankingDataRepository,
    BankingDataUnavailableError,
    ChequeIssuanceRecord,
)
from app.services.validation.models import CheckResult

VALID_CHEQUE_STATUSES = ("ISSUED", "PRESENTED", "PAID", "STOPPED", "CANCELLED", "EXPIRED")


def check_cheque_series(cheque_number: str | None, account: AccountRecord | None) -> CheckResult:
    severity = settings.validation_severities.get("CHEQUE_SERIES", "MEDIUM")

    if account is None:
        return CheckResult(
            "CHEQUE_SERIES", "NOT_CHECKED", severity,
            "Cheque series cannot be verified because the account was not found.",
        )
    if not cheque_number:
        return CheckResult(
            "CHEQUE_SERIES", "NOT_CHECKED", severity,
            "Cheque number not available from extracted data.",
        )

    try:
        number = int(cheque_number)
        start = int(account.cheque_series_start)
        end = int(account.cheque_series_end)
    except ValueError:
        return CheckResult(
            "CHEQUE_SERIES", "FAIL", severity,
            f"Cheque number '{cheque_number}' is not a valid numeric cheque number.",
        )

    if start <= number <= end:
        return CheckResult("CHEQUE_SERIES", "PASS", "INFO", "Cheque number is within the account's issued series.")

    return CheckResult(
        "CHEQUE_SERIES", "FAIL", severity,
        f"Cheque number {cheque_number} falls outside the account's expected series "
        f"[{account.cheque_series_start}-{account.cheque_series_end}].",
        details={"expected_range": [account.cheque_series_start, account.cheque_series_end]},
    )


def check_cheque_status(
    account_number: str | None, cheque_number: str | None, banking_repo: BankingDataRepository,
) -> tuple[CheckResult, ChequeIssuanceRecord | None]:
    severity = settings.validation_severities.get("CHEQUE_STATUS", "HIGH")
    stopped_severity = settings.validation_severities.get("CHEQUE_STATUS_STOPPED", "CRITICAL")

    if not account_number or not cheque_number:
        return CheckResult(
            "CHEQUE_STATUS", "NOT_CHECKED", severity,
            "Cheque status cannot be verified without both an account number and a cheque number.",
        ), None

    try:
        issuance = banking_repo.get_cheque_issuance(account_number, cheque_number)
    except BankingDataUnavailableError as exc:
        return CheckResult(
            "CHEQUE_STATUS", "NOT_CHECKED", severity, f"Banking data unavailable: {exc}",
        ), None

    if issuance is None:
        return CheckResult(
            "CHEQUE_STATUS", "FAIL", severity,
            f"No issuance record found for cheque number {cheque_number} on this account.",
        ), None

    if issuance.status == "ISSUED":
        return CheckResult("CHEQUE_STATUS", "PASS", "INFO", "Cheque status is ISSUED."), issuance

    if issuance.status == "STOPPED":
        return CheckResult(
            "CHEQUE_STATUS", "FAIL", stopped_severity,
            "Cheque has a STOPPED status in the bank's issuance registry.",
            details={"cheque_status": issuance.status},
        ), issuance

    return CheckResult(
        "CHEQUE_STATUS", "FAIL", severity,
        f"Cheque status is {issuance.status}; expected ISSUED.",
        details={"cheque_status": issuance.status},
    ), issuance
