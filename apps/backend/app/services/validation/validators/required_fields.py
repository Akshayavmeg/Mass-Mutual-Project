"""REQUIRED_FIELDS check (docs/16_Validation_Engine.md S9)."""

from __future__ import annotations

from app.core.config import settings
from app.services.validation.models import CheckResult

REQUIRED_FIELDS = ("cheque_number", "account_number", "amount", "date", "payee_name")


def check_required_fields(fields: dict) -> CheckResult:
    missing = [name for name in REQUIRED_FIELDS if not fields.get(name, {}).get("value")]
    severity = settings.validation_severities.get("REQUIRED_FIELDS", "HIGH")

    if missing:
        # docs/16 S9: a missing required field should route toward manual
        # review, not automatic rejection -- it may be an OCR failure
        # rather than an actually invalid cheque. FAIL is still the
        # correct *check* status (the data genuinely isn't usable); it is
        # the Decision Engine's job (Milestone 7) to route FAIL here to
        # REVIEW rather than REJECT.
        return CheckResult(
            "REQUIRED_FIELDS", "FAIL", severity,
            f"Missing required field(s): {', '.join(missing)}.",
            details={"missing_fields": missing},
        )
    return CheckResult("REQUIRED_FIELDS", "PASS", "INFO", "All required fields are present.")
