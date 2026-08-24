"""PAYEE_MATCH check (docs/16_Validation_Engine.md S17-S19).

Only whitespace/case normalization is applied before comparison -- no
aggressive fuzzy matching, per docs/16 S19: "it should not perform
aggressive fuzzy matching without carefully defined rules."
"""

from __future__ import annotations

import re

from app.core.config import settings
from app.repositories.banking_repository import ChequeIssuanceRecord
from app.services.validation.models import CheckResult


def _normalize_for_comparison(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def check_payee_match(payee_value: str | None, issuance: ChequeIssuanceRecord | None) -> CheckResult:
    severity = settings.validation_severities.get("PAYEE_MATCH", "HIGH")

    if not payee_value:
        return CheckResult(
            "PAYEE_MATCH", "NOT_CHECKED", severity, "Payee not available from extracted data.",
        )
    if issuance is None:
        return CheckResult(
            "PAYEE_MATCH", "NOT_CHECKED", severity,
            "Payee cannot be verified without a matching cheque issuance record.",
        )

    expected = issuance.payee_name
    if _normalize_for_comparison(payee_value) == _normalize_for_comparison(expected):
        return CheckResult("PAYEE_MATCH", "PASS", "INFO", "Extracted payee matches the expected banking record.")

    return CheckResult(
        "PAYEE_MATCH", "FAIL", severity,
        f"Extracted payee '{payee_value}' does not match the expected payee '{expected}'.",
        details={"extracted_payee": payee_value, "expected_payee": expected},
    )
