"""Decision rule evaluation (docs/22_Decision_Engine.md S8-S11: hard
rules first, then risk-score fallback).

Rule precedence (matches docs/22 S9's three-priority hierarchy exactly;
where docs/22 gives an example rather than an exact algorithm -- e.g.
which numeric tampering score counts as "severe" vs "suspicious" -- the
chosen implementation is documented inline and the threshold is
configurable, per this milestone's instructions):

    Priority 1 -- Critical Rejection Rules   -> REJECT
    Priority 2 -- Mandatory Review Rules     -> REVIEW
    Priority 3 -- Risk-score fallback        -> APPROVE / REVIEW / REJECT

All conditions are evaluated from already-computed Milestone 4-6 results
only -- this module performs no validation, fraud, signature, anomaly,
or risk computation of its own, and reuses Milestone 6's own
`risk_assessment.hard_rules_triggered` for the account-invalid/
confirmed-duplicate conditions rather than re-deriving them a third
time.
"""

from __future__ import annotations

from app.core.config import settings

# docs/22 S9 Priority 1: "confirmed_fraud" has no separate boolean
# anywhere in the pipeline -- the closest real, non-fabricated signal is
# the Fraud Detection Engine's own CRITICAL risk_level classification
# (docs/17's fraud engine, Milestone 5), which is what STOPPED_CHEQUE/
# multiple CRITICAL rule violations actually produce.
_CONFIRMED_FRAUD_LEVEL = "CRITICAL"

# Explicit, conservative policy choice (per this milestone's instruction
# #3): a signature mismatch/uncertainty of ANY severity (including the
# comparator's own CRITICAL band) routes to REVIEW, never REJECT --
# docs/22's own examples never show a signature result driving an
# automatic rejection, and Milestone 6's own calibration report found
# this comparator's separation too weak to trust as sole grounds for
# rejection.
_SIGNATURE_REVIEW_LEVELS = ("UNAVAILABLE", "MEDIUM", "HIGH", "CRITICAL")


def evaluate(
    *, validation: dict | None, fraud_analysis: dict, signature_analysis: dict | None,
    anomaly_analysis: dict | None, risk_assessment: dict, ocr_confidence: float | None,
) -> tuple[str, list[str], list[str], str | None]:
    """Returns (decision, triggered_rules, reasons, escalation_reason)."""
    triggered: list[str] = []
    reasons: list[str] = []

    hard_rules = risk_assessment.get("hard_rules_triggered", [])
    duplicate_status = (fraud_analysis.get("duplicate_analysis") or {}).get("duplicate_status", "NEW")
    tampering_score = (fraud_analysis.get("image_analysis") or {}).get("image_tampering_score")
    fraud_risk_level = fraud_analysis.get("risk_level", "LOW")
    tampering_cutoffs = settings.risk_tampering_score_cutoffs

    # --- Priority 1: Critical Rejection Rules --------------------------
    if "INVALID_OR_INACTIVE_ACCOUNT" in hard_rules:
        triggered.append("ACCOUNT_INVALID_HARD_REJECT")
        reasons.append("Account is invalid, closed, blocked, or otherwise not active.")
    if "CONFIRMED_DUPLICATE_CHEQUE" in hard_rules or duplicate_status == "CONFIRMED_DUPLICATE":
        triggered.append("CONFIRMED_DUPLICATE_HARD_REJECT")
        reasons.append("Confirmed duplicate cheque detected -- this hard rule overrides the numerical risk score.")
    if tampering_score is not None and tampering_score >= tampering_cutoffs["HIGH"]:
        triggered.append("SEVERE_TAMPERING_HARD_REJECT")
        reasons.append(f"Strong image tampering evidence detected (score={tampering_score:.2f}).")
    if fraud_risk_level == _CONFIRMED_FRAUD_LEVEL:
        triggered.append("CRITICAL_FRAUD_HARD_REJECT")
        reasons.append("Fraud Detection Engine classified this cheque as CRITICAL risk.")

    if triggered:
        return "REJECT", triggered, reasons, reasons[0]

    # --- Priority 2: Mandatory Review Rules -----------------------------
    if duplicate_status == "POTENTIAL_DUPLICATE":
        triggered.append("POSSIBLE_DUPLICATE_REVIEW")
        reasons.append("Duplicate evidence is potential rather than confirmed.")

    signature_risk_level = (signature_analysis or {}).get("risk_level")
    if signature_analysis is None or signature_risk_level in _SIGNATURE_REVIEW_LEVELS:
        triggered.append("SIGNATURE_UNCERTAIN_REVIEW")
        if signature_analysis is None:
            reasons.append("Signature analysis has not been run.")
        elif signature_risk_level == "UNAVAILABLE":
            reasons.append("Signature verification is unavailable (no usable reference) -- not treated as fraud, but requires review.")
        else:
            reasons.append(f"Signature verification produced a {signature_risk_level.lower()}-confidence result.")

    if tampering_score is not None and tampering_cutoffs["LOW"] <= tampering_score < tampering_cutoffs["HIGH"]:
        triggered.append("SUSPICIOUS_TAMPERING_REVIEW")
        reasons.append(f"Possible image tampering detected (score={tampering_score:.2f}).")

    if ocr_confidence is not None and ocr_confidence < settings.decision_min_ocr_confidence:
        triggered.append("LOW_OCR_CONFIDENCE_REVIEW")
        reasons.append(f"OCR confidence ({ocr_confidence:.1f}%) is below the configured review threshold.")

    validation_status = (validation or {}).get("overall_validation_status")
    if validation_status not in ("PASS", None) or validation is None:
        triggered.append("VALIDATION_ISSUE_REVIEW")
        if validation is None:
            reasons.append("Validation has not been run.")
        else:
            reasons.append(f"Validation overall status is {validation_status}, not PASS.")

    unavailable_inputs = risk_assessment.get("unavailable_inputs", [])
    if unavailable_inputs:
        triggered.append("CRITICAL_DATA_UNAVAILABLE_REVIEW")
        reasons.append(f"Required verification data unavailable: {', '.join(unavailable_inputs)}.")

    anomaly_risk_level = (anomaly_analysis or {}).get("risk_level")
    if anomaly_analysis is None or anomaly_risk_level in ("HIGH", "CRITICAL"):
        triggered.append("UNUSUAL_ANOMALY_REVIEW")
        reasons.append(
            "Anomaly analysis has not been run." if anomaly_analysis is None else
            f"Anomaly risk level is {anomaly_risk_level}."
        )

    fraud_indicators = fraud_analysis.get("indicators", [])
    high_risk_count = sum(1 for ind in fraud_indicators if ind.get("severity") in ("HIGH", "CRITICAL"))
    if high_risk_count >= settings.fraud_multi_indicator_review_threshold:
        triggered.append("MULTIPLE_HIGH_RISK_INDICATORS_REVIEW")
        reasons.append(f"{high_risk_count} high-or-critical-severity fraud indicators were detected.")

    if triggered:
        return "REVIEW", triggered, reasons, reasons[0]

    # --- Priority 3: Risk-score fallback (reuses Milestone 6's own
    # risk_level rather than re-deriving numeric cutoffs) --------------
    risk_level = risk_assessment.get("risk_level", "CRITICAL")
    if risk_level == "LOW":
        return "APPROVE", ["LOW_RISK_APPROVE"], ["All mandatory validation checks passed and no fraud indicators were detected; risk score is within the low-risk range."], None
    if risk_level == "CRITICAL":
        return "REJECT", ["CRITICAL_RISK_REJECT"], ["Overall risk score is in the critical range."], "Overall risk score is in the critical range."
    return "REVIEW", ["RISK_SCORE_REVIEW"], [f"Overall risk level is {risk_level}, requiring manual verification."], f"Overall risk level is {risk_level}, requiring manual verification."
