"""Dashboard aggregation service (docs/26_API_Specification.md S27-S29,
docs/30_Dashboard_and_Reporting.md).

docs/26 documents these three dashboard endpoints but no milestone before
this one implemented them (M0-M8 built the underlying cheque-processing
data, not the aggregation layer). Milestone 9's own instructions
explicitly authorize filling exactly this kind of gap: "If an aggregate
API does not currently exist: identify the gap, implement the minimum
documented backend/API support required, keep it consistent with
docs/26, do not silently fabricate dashboard metrics."

Every number here is computed live from the already-persisted cheque
records (via the same repository used by every other milestone) --
nothing is hard-coded or estimated. Averages/rates are None (not 0) when
there is no data to compute them from, so the frontend can distinguish
"zero" from "unavailable" rather than a misleading 0%.
"""

from __future__ import annotations

from datetime import datetime

from app.repositories.cheque_repository import get_cheque_repository

_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def get_summary() -> dict:
    records = get_cheque_repository().list_all()
    total = len(records)
    approved = under_review = rejected = fraud_detected = 0
    processing_durations: list[float] = []
    ocr_confidences: list[float] = []

    for record in records:
        status = record.get("processing_status")
        decision = record.get("decision") or {}
        human_decision = record.get("human_decision") or {}
        final_decision = human_decision.get("decision") or decision.get("decision")

        if status == "UNDER_REVIEW" or (decision.get("decision") == "REVIEW" and not human_decision):
            under_review += 1
        elif final_decision == "APPROVE" or status == "APPROVED":
            approved += 1
        elif final_decision == "REJECT" or status == "REJECTED":
            rejected += 1

        fraud_analysis = record.get("fraud_analysis") or {}
        if fraud_analysis.get("risk_level") in ("HIGH", "CRITICAL"):
            fraud_detected += 1

        upload_ts = _parse_iso(record.get("upload_timestamp"))
        decision_ts = _parse_iso(decision.get("decision_timestamp"))
        if upload_ts is not None and decision_ts is not None:
            processing_durations.append((decision_ts - upload_ts).total_seconds())

        ocr = record.get("ocr") or {}
        if ocr.get("average_confidence") is not None:
            ocr_confidences.append(ocr["average_confidence"])

    return {
        "total_cheques": total,
        "approved": approved,
        "under_review": under_review,
        "rejected": rejected,
        "fraud_detected": fraud_detected,
        "average_processing_time_seconds": (
            round(sum(processing_durations) / len(processing_durations), 3) if processing_durations else None
        ),
        "average_ocr_confidence": (
            round(sum(ocr_confidences) / len(ocr_confidences), 2) if ocr_confidences else None
        ),
    }


def get_fraud_statistics() -> dict:
    records = get_cheque_repository().list_all()
    counts = {level: 0 for level in _RISK_LEVELS}
    for record in records:
        risk_assessment = record.get("risk_assessment")
        risk_level = (risk_assessment or {}).get("risk_level")
        if risk_level in counts:
            counts[risk_level] += 1
    return {
        "low_risk": counts["LOW"],
        "medium_risk": counts["MEDIUM"],
        "high_risk": counts["HIGH"],
        "critical_risk": counts["CRITICAL"],
    }


def get_processing_statistics() -> dict:
    records = get_cheque_repository().list_all()
    processing_durations: list[float] = []
    ocr_total = ocr_success = 0
    validation_total = validation_success = 0
    decision_total = review_count = 0

    for record in records:
        upload_ts = _parse_iso(record.get("upload_timestamp"))
        decision = record.get("decision") or {}
        decision_ts = _parse_iso(decision.get("decision_timestamp"))
        if upload_ts is not None and decision_ts is not None:
            processing_durations.append((decision_ts - upload_ts).total_seconds())

        ocr = record.get("ocr")
        if ocr is not None:
            ocr_total += 1
            if ocr.get("ocr_status") != "FAILED":
                ocr_success += 1

        validation = record.get("validation")
        if validation is not None:
            validation_total += 1
            if validation.get("overall_validation_status") == "PASS":
                validation_success += 1

        if decision:
            decision_total += 1
            if decision.get("decision") == "REVIEW":
                review_count += 1

    return {
        "average_processing_time": (
            round(sum(processing_durations) / len(processing_durations), 3) if processing_durations else None
        ),
        "ocr_success_rate": round(100.0 * ocr_success / ocr_total, 2) if ocr_total else None,
        "validation_success_rate": round(100.0 * validation_success / validation_total, 2) if validation_total else None,
        "manual_review_rate": round(100.0 * review_count / decision_total, 2) if decision_total else None,
    }
