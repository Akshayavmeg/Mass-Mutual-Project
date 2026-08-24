"""Decision Engine orchestrator (docs/22_Decision_Engine.md S1-S3).

Consumes Milestones 4-6's already-persisted results only -- performs no
new OCR, validation, fraud detection, signature analysis, anomaly
detection, or risk scoring itself (this milestone's explicit module
boundary). When the decision is REVIEW, automatically creates a Manual
Review case (docs/22 S22, docs/23 S4) as an internal side effect --
review-case creation has no separate canonical docs/26 endpoint of its
own, so this is how docs/23's documented "Decision Engine -> REVIEW ->
Create Review Case" flow is realized (see the Milestone 7 report for
the full reasoning).
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.repositories.cheque_repository import get_cheque_repository
from app.services.decision import decision_rules
from app.services.decision.exceptions import RiskAssessmentNotAvailableError
from app.services.decision.models import DecisionResult
from app.services.review import review_service


def _build_evidence(validation, fraud_analysis, signature_analysis, anomaly_analysis, risk_assessment, ocr) -> dict:
    return {
        "validation_status": (validation or {}).get("overall_validation_status"),
        "fraud_risk_level": fraud_analysis.get("risk_level"),
        "duplicate_status": (fraud_analysis.get("duplicate_analysis") or {}).get("duplicate_status"),
        "signature_risk_level": (signature_analysis or {}).get("risk_level"),
        "anomaly_risk_level": (anomaly_analysis or {}).get("risk_level"),
        "overall_risk_level": risk_assessment.get("risk_level"),
        "ocr_confidence": (ocr or {}).get("average_confidence"),
    }


def make_decision(cheque_id: str) -> DecisionResult:
    repo = get_cheque_repository()
    record = repo.get(cheque_id)
    if record is None:
        raise KeyError(cheque_id)

    risk_assessment = record.get("risk_assessment")
    if risk_assessment is None:
        raise RiskAssessmentNotAvailableError(
            "Cheque has not completed Milestone 6 risk scoring yet; a decision cannot be made."
        )

    validation = record.get("validation")
    fraud_analysis = record.get("fraud_analysis") or {}
    signature_analysis = record.get("signature_analysis")
    anomaly_analysis = record.get("anomaly_analysis")
    ocr = record.get("ocr")

    decision, triggered_rules, reasons, escalation_reason = decision_rules.evaluate(
        validation=validation, fraud_analysis=fraud_analysis, signature_analysis=signature_analysis,
        anomaly_analysis=anomaly_analysis, risk_assessment=risk_assessment,
        ocr_confidence=(ocr or {}).get("average_confidence"),
    )

    result = DecisionResult(
        cheque_id=cheque_id,
        decision=decision,
        decision_reason=reasons[0] if reasons else "No triggering condition recorded.",
        reasons=reasons,
        triggered_rules=triggered_rules,
        risk_score=risk_assessment.get("overall_risk_score", 0.0),
        risk_level=risk_assessment.get("risk_level", "CRITICAL"),
        requires_manual_review=(decision == "REVIEW"),
        escalation_reason=escalation_reason if decision != "APPROVE" else None,
        unavailable_inputs=risk_assessment.get("unavailable_inputs", []),
        ruleset_version=settings.decision_engine_version,
        policy_version=settings.decision_policy_version,
        decision_timestamp=datetime.now(timezone.utc).isoformat(),
        evidence=_build_evidence(validation, fraud_analysis, signature_analysis, anomaly_analysis, risk_assessment, ocr),
    )

    repo.update(cheque_id, {"decision": result.as_dict(), "processing_status": "DECISION_MADE" if decision != "REVIEW" else "UNDER_REVIEW"})

    if decision == "REVIEW":
        review_service.create_review_case(cheque_id, decision_result=result.as_dict(), record=record)

    return result


def get_decision(cheque_id: str) -> dict | None:
    record = get_cheque_repository().get(cheque_id)
    if record is None:
        return None
    return record.get("decision")
