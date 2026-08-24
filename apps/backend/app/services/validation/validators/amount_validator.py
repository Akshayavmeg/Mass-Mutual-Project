"""AMOUNT / AMOUNT_CONSISTENCY checks (docs/16_Validation_Engine.md
S21-S22)."""

from __future__ import annotations

from app.core.config import settings
from app.services.validation.amount_words import words_to_amount
from app.services.validation.models import CheckResult


def check_amount(amount_value: float | None) -> CheckResult:
    severity = settings.validation_severities.get("AMOUNT", "HIGH")

    if amount_value is None:
        return CheckResult("AMOUNT", "NOT_CHECKED", severity, "Amount not available from extracted data.")

    if amount_value <= 0:
        return CheckResult(
            "AMOUNT", "FAIL", severity, f"Amount {amount_value} must be greater than zero.",
        )

    if amount_value > settings.max_permitted_cheque_amount:
        return CheckResult(
            "AMOUNT", "FAIL", severity,
            f"Amount {amount_value} exceeds the configured maximum permitted amount of "
            f"{settings.max_permitted_cheque_amount}.",
            details={"amount": amount_value, "max_permitted": settings.max_permitted_cheque_amount},
        )

    return CheckResult("AMOUNT", "PASS", "INFO", "Amount is valid and within configured limits.")


def check_amount_consistency(amount_value: float | None, amount_in_words_value: str | None) -> CheckResult:
    severity = settings.validation_severities.get("AMOUNT_CONSISTENCY", "HIGH")

    if amount_value is None or not amount_in_words_value:
        return CheckResult(
            "AMOUNT_CONSISTENCY", "NOT_CHECKED", severity,
            "Amount consistency cannot be verified without both a numeric amount and an amount in words.",
        )

    words_amount = words_to_amount(amount_in_words_value)
    if words_amount is None:
        return CheckResult(
            "AMOUNT_CONSISTENCY", "WARNING", severity,
            f"Amount in words ('{amount_in_words_value}') could not be interpreted for comparison.",
        )

    if abs(words_amount - amount_value) < 0.01:
        return CheckResult(
            "AMOUNT_CONSISTENCY", "PASS", "INFO", "Numeric amount matches the amount in words.",
        )

    return CheckResult(
        "AMOUNT_CONSISTENCY", "FAIL", severity,
        f"Numeric amount ({amount_value}) does not match the amount in words "
        f"('{amount_in_words_value}' = {words_amount}).",
        details={"numeric_amount": amount_value, "words_amount": words_amount},
    )
