"""Overall Risk Scoring orchestrator (docs/21_Risk_Scoring.md S7, S14).

Combines validation (M4), fraud/tampering/duplicate (M5), signature and
anomaly (M6), and OCR-confidence (M3) signals into ONE explainable
0-100 overall_risk_score -- distinct from Milestone 5's own
fraud_results.fraud_score (docs/25's schema keeps these as separate
tables/concepts; see the Milestone 5 and 6 reports). This module does
not recompute or duplicate any upstream detector's logic -- it only
reads their already-persisted results and maps each into a bounded
contribution per docs/21 S7-S13's factor table.

Module boundary (docs/21 S1, S30-S31): produces a risk score and
contributing-factor breakdown for the Decision Engine (Milestone 7) --
never an APPROVE/REVIEW/REJECT decision itself. Hard rules (docs/21
S17-S18) only ESCALATE the risk_level classification here; they do not
produce a decision verdict.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.repositories.cheque_repository import get_cheque_repository
from app.services.audit import audit_service
from app.services.risk.exceptions import FraudAnalysisNotAvailableError
from app.services.risk.models import RiskAssessmentResult, RiskFactor

_RISK_PRECEDENCE = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def _tampering_factor(fraud_analysis: dict) -> RiskFactor:
    weight = settings.risk_factor_weights["tampering"]
    score = (fraud_analysis.get("image_analysis") or {}).get("image_tampering_score")
    if score is None:
        return RiskFactor("TAMPERING", 0.0, weight, "Image tampering analysis unavailable.", {"image_tampering_score": None})

    cutoffs = settings.risk_tampering_score_cutoffs
    bands = settings.risk_tampering_contribution_bands
    if score < cutoffs["NONE"]:
        band = "NONE"
    elif score < cutoffs["LOW"]:
        band = "LOW"
    elif score < cutoffs["MODERATE"]:
        band = "MODERATE"
    elif score < cutoffs["HIGH"]:
        band = "HIGH"
    else:
        band = "STRONG"
    contribution = bands[band]
    return RiskFactor(
        "TAMPERING", contribution, weight,
        f"Image tampering score {score:.2f} classified as {band}.",
        {"image_tampering_score": round(score, 4), "band": band},
    )


def _signature_factor(signature_analysis: dict | None) -> tuple[RiskFactor, bool]:
    weight = settings.risk_factor_weights["signature"]
    if signature_analysis is None:
        return RiskFactor("SIGNATURE", 0.0, weight, "Signature analysis has not been run.", None), True

    risk_level = signature_analysis.get("risk_level", "UNAVAILABLE")
    bands = settings.risk_signature_contribution_bands
    contribution = bands.get(risk_level, 0.0)
    unavailable = risk_level == "UNAVAILABLE"
    reason = (
        "Signature verification unavailable (no usable reference or unreliable image) -- not treated as fraud."
        if unavailable else
        f"Signature similarity risk level: {risk_level} (similarity={signature_analysis.get('similarity_score')})."
    )
    return RiskFactor("SIGNATURE", contribution, weight, reason, {"signature_risk_level": risk_level}), unavailable


def _duplicate_factor(fraud_analysis: dict) -> RiskFactor:
    weight = settings.risk_factor_weights["duplicate"]
    status = (fraud_analysis.get("duplicate_analysis") or {}).get("duplicate_status", "NEW")
    contribution = settings.risk_duplicate_contribution_bands.get(status, 0.0)
    return RiskFactor("DUPLICATE", contribution, weight, f"Duplicate status: {status}.", {"duplicate_status": status})


def _anomaly_factor(anomaly_analysis: dict | None) -> tuple[RiskFactor, bool]:
    weight = settings.risk_factor_weights["anomaly"]
    if anomaly_analysis is None:
        return RiskFactor("ANOMALY", 0.0, weight, "Anomaly analysis has not been run.", None), True
    score = anomaly_analysis.get("anomaly_score", 0.0)
    contribution = min(weight, (score / 100.0) * weight)
    unavailable = anomaly_analysis.get("analysis_status") == "INSUFFICIENT_DATA"
    reason = f"Anomaly score {score:.1f}/100 scaled into the {weight:.0f}-point risk-factor budget."
    return RiskFactor("ANOMALY", contribution, weight, reason, {"anomaly_score": score}), unavailable


def _validation_factor(validation: dict | None) -> RiskFactor:
    weight = settings.risk_factor_weights["validation"]
    if validation is None:
        return RiskFactor("VALIDATION", weight, weight, "Validation has not been run.", None)
    status = validation.get("overall_validation_status", "FAIL")
    band = "PASS" if status == "PASS" else "WARNING" if status == "WARNING" else "FAIL"
    contribution = settings.risk_validation_contribution_bands[band]
    return RiskFactor("VALIDATION", contribution, weight, f"Validation overall status: {status}.", {"overall_validation_status": status})


def _ocr_factor(ocr: dict | None) -> RiskFactor:
    weight = settings.risk_factor_weights["ocr"]
    if ocr is None:
        return RiskFactor("OCR", weight, weight, "OCR has not been run.", None)
    confidence = ocr.get("average_confidence", 0.0)
    bands = settings.risk_ocr_confidence_contribution_bands
    if confidence >= 95:
        contribution = bands["95"]
    elif confidence >= 85:
        contribution = bands["85"]
    elif confidence >= 70:
        contribution = bands["70"]
    else:
        contribution = bands["0"]
    return RiskFactor("OCR", contribution, weight, f"OCR average confidence: {confidence:.1f}%.", {"average_confidence": confidence})


def calculate_risk(cheque_id: str) -> RiskAssessmentResult:
    repo = get_cheque_repository()
    record = repo.get(cheque_id)
    if record is None:
        raise KeyError(cheque_id)

    fraud_analysis = record.get("fraud_analysis")
    if fraud_analysis is None:
        raise FraudAnalysisNotAvailableError(
            "Cheque has not completed Milestone 5 fraud analysis yet; risk scoring cannot run."
        )

    signature_analysis = record.get("signature_analysis")
    anomaly_analysis = record.get("anomaly_analysis")
    validation = record.get("validation")
    ocr = record.get("ocr")

    unavailable_inputs: list[str] = []
    signature_factor, signature_unavailable = _signature_factor(signature_analysis)
    anomaly_factor, anomaly_unavailable = _anomaly_factor(anomaly_analysis)
    if signature_unavailable:
        unavailable_inputs.append("SIGNATURE_ANALYSIS")
    if anomaly_unavailable:
        unavailable_inputs.append("ANOMALY_ANALYSIS")
    if validation is None:
        unavailable_inputs.append("VALIDATION")
    if ocr is None:
        unavailable_inputs.append("OCR")

    factors = [
        _tampering_factor(fraud_analysis),
        signature_factor,
        _duplicate_factor(fraud_analysis),
        anomaly_factor,
        _validation_factor(validation),
        _ocr_factor(ocr),
        RiskFactor("OTHER", 0.0, settings.risk_factor_weights["other"], "No additional documented signal source defined for this MVP.", None),
    ]

    overall_score = min(100.0, sum(f.contribution for f in factors))
    risk_level = _classify(overall_score)

    # Hard rules (docs/21 S17-S18): some conditions escalate risk
    # classification regardless of the numeric score, but still do not
    # produce a decision -- that remains Milestone 7's responsibility.
    hard_rules: list[str] = []
    duplicate_status = (fraud_analysis.get("duplicate_analysis") or {}).get("duplicate_status")
    if duplicate_status == "CONFIRMED_DUPLICATE":
        hard_rules.append("CONFIRMED_DUPLICATE_CHEQUE")
    if validation is not None:
        account_status_check = (validation.get("checks") or {}).get("ACCOUNT_STATUS", {})
        account_exists_check = (validation.get("checks") or {}).get("ACCOUNT_EXISTS", {})
        if account_status_check.get("status") == "FAIL" or account_exists_check.get("status") == "FAIL":
            hard_rules.append("INVALID_OR_INACTIVE_ACCOUNT")

    if hard_rules and _RISK_PRECEDENCE[risk_level] < _RISK_PRECEDENCE["HIGH"]:
        risk_level = "HIGH"

    result = RiskAssessmentResult(
        cheque_id=cheque_id, overall_risk_score=overall_score, risk_level=risk_level,
        risk_factors=factors, hard_rules_triggered=hard_rules, unavailable_inputs=unavailable_inputs,
        config_version=settings.risk_config_version, analysis_timestamp=datetime.now(timezone.utc).isoformat(),
    )

    repo.update(cheque_id, {"risk_assessment": result.as_dict(), "processing_status": "RISK_SCORED"})
    audit_service.record(
        event_type="RISK_SCORE_GENERATED", cheque_id=cheque_id, source="SYSTEM",
        new_status="RISK_SCORED", action="CALCULATE_RISK", result=risk_level,
        metadata={"overall_risk_score": overall_score},
    )
    return result


def _classify(score: float) -> str:
    for level in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        low, high = settings.risk_bands[level]
        if low <= score <= high:
            return level
    return "CRITICAL"


def get_risk_result(cheque_id: str) -> dict | None:
    record = get_cheque_repository().get(cheque_id)
    if record is None:
        return None
    return record.get("risk_assessment")
