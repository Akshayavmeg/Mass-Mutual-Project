"""DATE_WINDOW check (docs/16_Validation_Engine.md S14-S16)."""

from __future__ import annotations

from datetime import date

from app.core.config import settings
from app.services.validation.models import CheckResult


def check_date_window(date_value: str | None, processing_date: date) -> CheckResult:
    """`processing_date` is passed in explicitly (rather than read from
    `date.today()` internally) so this check is deterministic and
    testable, per this milestone's requirement."""
    severity = settings.validation_severities.get("DATE_WINDOW", "MEDIUM")

    if not date_value:
        return CheckResult(
            "DATE_WINDOW", "NOT_CHECKED", severity, "Date not available from extracted data.",
        )

    try:
        cheque_date = date.fromisoformat(date_value)
    except ValueError:
        return CheckResult(
            "DATE_WINDOW", "FAIL", severity, f"'{date_value}' is not a valid date.",
        )

    if cheque_date > processing_date and not settings.allow_future_dated_cheques:
        return CheckResult(
            "DATE_WINDOW", "FAIL", severity,
            f"Cheque is future-dated ({date_value} is after the processing date {processing_date.isoformat()}).",
            details={"cheque_date": date_value, "processing_date": processing_date.isoformat()},
        )

    age_days = (processing_date - cheque_date).days
    if age_days > settings.cheque_validity_period_days:
        return CheckResult(
            "DATE_WINDOW", "FAIL", severity,
            f"Cheque is {age_days} days old, exceeding the configured validity window of "
            f"{settings.cheque_validity_period_days} days.",
            details={"age_days": age_days, "validity_period_days": settings.cheque_validity_period_days},
        )

    return CheckResult("DATE_WINDOW", "PASS", "INFO", "Cheque date is within the configured processing window.")
