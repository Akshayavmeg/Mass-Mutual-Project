"""ACCOUNT_EXISTS / ACCOUNT_STATUS checks (docs/16_Validation_Engine.md
S10-S11)."""

from __future__ import annotations

from app.core.config import settings
from app.repositories.banking_repository import (
    AccountRecord,
    BankingDataRepository,
    BankingDataUnavailableError,
)
from app.services.validation.models import CheckResult

VALID_ACCOUNT_STATUSES = ("ACTIVE", "INACTIVE", "CLOSED", "BLOCKED", "FROZEN")


def check_account_exists(
    account_number: str | None, banking_repo: BankingDataRepository,
) -> tuple[CheckResult, AccountRecord | None]:
    severity = settings.validation_severities.get("ACCOUNT_EXISTS", "HIGH")

    if not account_number:
        return CheckResult(
            "ACCOUNT_EXISTS", "NOT_CHECKED", severity,
            "Account number not available from extracted data.",
        ), None

    try:
        account = banking_repo.get_account(account_number)
    except BankingDataUnavailableError as exc:
        # Fail-safe (docs/16 S42): a data-source failure must never be
        # silently treated as PASS.
        return CheckResult(
            "ACCOUNT_EXISTS", "NOT_CHECKED", severity,
            f"Banking data unavailable: {exc}",
        ), None

    if account is None:
        return CheckResult(
            "ACCOUNT_EXISTS", "FAIL", severity,
            f"Account {account_number} was not found in banking records.",
        ), None

    return CheckResult(
        "ACCOUNT_EXISTS", "PASS", "INFO", "Account exists in banking records.",
    ), account


def check_account_status(account: AccountRecord | None) -> CheckResult:
    severity = settings.validation_severities.get("ACCOUNT_STATUS", "HIGH")

    if account is None:
        return CheckResult(
            "ACCOUNT_STATUS", "NOT_CHECKED", severity,
            "Account status cannot be verified because the account was not found.",
        )

    if account.account_status == "ACTIVE":
        return CheckResult("ACCOUNT_STATUS", "PASS", "INFO", "Account status is ACTIVE.")

    return CheckResult(
        "ACCOUNT_STATUS", "FAIL", severity,
        f"Account status is {account.account_status}; expected ACTIVE.",
        details={"account_status": account.account_status},
    )
