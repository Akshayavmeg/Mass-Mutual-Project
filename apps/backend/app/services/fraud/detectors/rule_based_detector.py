"""Rule-based fraud detector (docs/17_Fraud_Detection.md S19 RULE-001 -
RULE-005; S13-S18 validation-based fraud signals).

Consumes the Milestone 4 ValidationSummary (as persisted on the cheque
record) rather than re-deriving any banking checks itself -- this
detector only translates already-computed validation results, a
duplicate-detection result, and an (in this milestone, always
unavailable) signature-analysis result into fraud indicators.
"""

from __future__ import annotations

from app.core.config import settings
from app.services.fraud.models import FraudIndicator, RuleViolation

# docs/17 S20 example severity table.
_STOPPED_CHEQUE_SEVERITY = "CRITICAL"


def _check_status(validation_checks: dict, name: str) -> str | None:
    check = validation_checks.get(name)
    return check.get("status") if check else None


def evaluate(
    *,
    validation_checks: dict,
    duplicate_status: str,
    signature_result: dict | None,
) -> tuple[list[FraudIndicator], list[RuleViolation]]:
    """`duplicate_status` is one of NEW/POTENTIAL_DUPLICATE/CONFIRMED_DUPLICATE
    from the duplicate detector. `signature_result`, when provided, is
    expected to look like {"status": "MATCH"|"MISMATCH"|..., "similarity_score": float}
    -- docs/18_Signature_Analysis.md's module is Milestone 6's
    responsibility, so in normal Milestone 5 operation this is always
    None and RULE-003 cannot fire; the parameter exists purely so the
    interface is ready for Milestone 6 to supply a real result later."""
    weights = settings.fraud_score_weights
    indicators: list[FraudIndicator] = []
    violations: list[RuleViolation] = []

    account_exists_fail = _check_status(validation_checks, "ACCOUNT_EXISTS") == "FAIL"
    account_status_fail = _check_status(validation_checks, "ACCOUNT_STATUS") == "FAIL"
    cheque_series_fail = _check_status(validation_checks, "CHEQUE_SERIES") == "FAIL"
    cheque_status = validation_checks.get("CHEQUE_STATUS", {})
    cheque_status_fail = cheque_status.get("status") == "FAIL"
    cheque_stopped = bool(cheque_status.get("details") and cheque_status["details"].get("cheque_status") == "STOPPED")
    routing_fail = _check_status(validation_checks, "ROUTING_TRANSIT") == "FAIL"
    date_fail = _check_status(validation_checks, "DATE_WINDOW") == "FAIL"
    payee_fail = _check_status(validation_checks, "PAYEE_MATCH") == "FAIL"
    amount_consistency_fail = _check_status(validation_checks, "AMOUNT_CONSISTENCY") == "FAIL"
    amount_invalid_fail = _check_status(validation_checks, "AMOUNT") == "FAIL"

    # RULE-001: account does not exist -> significant risk increase.
    if account_exists_fail:
        indicators.append(FraudIndicator(
            type="ACCOUNT_MISMATCH", severity="CRITICAL",
            reason="Account does not exist in banking records.",
            contribution=weights["validation_signal"],
        ))
        violations.append(RuleViolation(
            "RULE-001", "IF account does not exist THEN increase risk significantly.",
            triggered_by=["ACCOUNT_EXISTS"],
        ))
    elif account_status_fail:
        indicators.append(FraudIndicator(
            type="ACCOUNT_MISMATCH", severity="HIGH",
            reason="Account status is not ACTIVE (docs/17 S13: closed/blocked/frozen accounts are a strong risk indicator).",
            contribution=weights["validation_signal"] * 0.7,
        ))

    # RULE-002: cheque already processed -> duplicate risk marked high.
    if duplicate_status == "CONFIRMED_DUPLICATE":
        indicators.append(FraudIndicator(
            type="DUPLICATE_CHEQUE", severity="HIGH",
            reason="Cheque matches a previously processed record (confirmed duplicate).",
            contribution=weights["duplicate"],
        ))
        violations.append(RuleViolation(
            "RULE-002", "IF cheque is already processed THEN mark duplicate risk as high.",
            triggered_by=["DUPLICATE_CHECK"],
        ))
    elif duplicate_status == "POTENTIAL_DUPLICATE":
        indicators.append(FraudIndicator(
            type="DUPLICATE_CHEQUE", severity="MEDIUM",
            reason="Cheque shows strong similarity to a previously processed record (potential duplicate).",
            contribution=weights["duplicate"] * 0.5,
        ))

    # RULE-003: payee mismatch AND signature mismatch -> significant risk increase.
    signature_mismatch = bool(signature_result and signature_result.get("status") == "MISMATCH")
    if payee_fail and signature_mismatch:
        indicators.append(FraudIndicator(
            type="PAYEE_AND_SIGNATURE_MISMATCH", severity="CRITICAL",
            reason="Payee mismatch combined with signature mismatch.",
            contribution=weights["validation_signal"],
        ))
        violations.append(RuleViolation(
            "RULE-003", "IF payee mismatch AND signature mismatch THEN increase risk significantly.",
            triggered_by=["PAYEE_MATCH", "SIGNATURE_ANALYSIS"],
        ))
    elif payee_fail:
        indicators.append(FraudIndicator(
            type="PAYEE_MISMATCH", severity="HIGH",
            reason="Extracted payee does not match the expected banking record.",
            contribution=weights["validation_signal"] * 0.4,
        ))

    # RULE-004: amount mismatch -> high-priority alert.
    if amount_consistency_fail:
        indicators.append(FraudIndicator(
            type="AMOUNT_MISMATCH", severity="HIGH",
            reason="Numeric amount does not match the amount written in words.",
            contribution=weights["validation_signal"] * 0.6,
        ))
        violations.append(RuleViolation(
            "RULE-004", "IF amount mismatch THEN create high-priority alert.",
            triggered_by=["AMOUNT_CONSISTENCY"],
        ))
    elif amount_invalid_fail:
        indicators.append(FraudIndicator(
            type="AMOUNT_MISMATCH", severity="MEDIUM",
            reason="Cheque amount failed basic validity checks (non-positive or over the configured maximum).",
            contribution=weights["validation_signal"] * 0.3,
        ))

    if cheque_stopped:
        indicators.append(FraudIndicator(
            type="STOPPED_CHEQUE", severity=_STOPPED_CHEQUE_SEVERITY,
            reason="Cheque has a STOPPED status in the bank's issuance registry.",
            contribution=weights["validation_signal"],
        ))
    elif cheque_status_fail:
        indicators.append(FraudIndicator(
            type="CHEQUE_STATUS_MISMATCH", severity="HIGH",
            reason="Cheque status is not ISSUED.",
            contribution=weights["validation_signal"] * 0.5,
        ))

    if cheque_series_fail:
        indicators.append(FraudIndicator(
            type="CHEQUE_SERIES_MISMATCH", severity="MEDIUM",
            reason="Cheque number falls outside the account's expected issued series.",
            contribution=weights["validation_signal"] * 0.3,
        ))

    if routing_fail:
        indicators.append(FraudIndicator(
            type="ROUTING_MISMATCH", severity="MEDIUM",
            reason="Routing/transit number does not match the banking record.",
            contribution=weights["validation_signal"] * 0.2,
        ))

    if date_fail:
        indicators.append(FraudIndicator(
            type="DATE_ANOMALY", severity="MEDIUM",
            reason="Cheque date is future-dated, stale, or otherwise outside the configured processing window.",
            contribution=weights["validation_signal"] * 0.2,
        ))

    failed_check_count = sum(1 for c in validation_checks.values() if c.get("status") == "FAIL")
    if failed_check_count >= settings.validation_multiple_failures_threshold:
        indicators.append(FraudIndicator(
            type="MULTIPLE_VALIDATION_FAILURES", severity="HIGH",
            reason=f"{failed_check_count} independent validation checks failed simultaneously.",
            contribution=weights["validation_signal"] * 0.3,
            evidence={"failed_check_count": failed_check_count},
        ))

    return indicators, violations
