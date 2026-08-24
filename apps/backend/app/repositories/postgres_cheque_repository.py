"""PostgreSQL-backed implementation of ChequeRecordRepository (Milestone
8; docs/25_Database_Schema.md).

Implements the exact same Protocol interface as
app.repositories.cheque_repository.InMemoryChequeRepository (save/get/
update/list_all) so Milestones 3-7's service code does not change at
all -- only app.repositories.repository_factory decides which
implementation `get_cheque_repository()` hands back.

Each `updates` dict key from the existing services (e.g. "validation",
"fraud_analysis", "decision") is routed to its own normalized table via
`_UPDATE_HANDLERS`; unmapped keys are preserved verbatim in
`cheques.upload_metadata` so no data from the existing dict-shaped
records is silently dropped.
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

from sqlalchemy.orm import Session, sessionmaker

from app.core.database import SessionLocal
from app.models.cheque import Cheque
from app.models.processing_results import (
    AnomalyResult,
    Decision,
    DuplicateResult,
    FraudResult,
    OCRResult,
    RiskAssessment,
    SignatureResult,
    ValidationResult,
)

_KNOWN_TOP_LEVEL_KEYS = {
    "cheque_id", "extraction", "ocr", "validation", "fraud_analysis",
    "signature_analysis", "anomaly_analysis", "risk_assessment", "decision",
}


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return date_type.fromisoformat(value)
    except ValueError:
        return None


class PostgresChequeRepository:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    # -- public Protocol surface ----------------------------------------

    def save(self, cheque_id: str, record: dict) -> None:
        with self._session_factory() as session:
            cheque = session.get(Cheque, cheque_id)
            if cheque is None:
                cheque = Cheque(cheque_id=cheque_id, image_path="", file_type="")
                session.add(cheque)
            self._apply_top_level(cheque, record)
            for key, value in record.items():
                if key not in _KNOWN_TOP_LEVEL_KEYS or value is None:
                    continue
                self._route_update(session, cheque, key, value)
            session.commit()

    def get(self, cheque_id: str) -> dict | None:
        with self._session_factory() as session:
            cheque = session.get(Cheque, cheque_id)
            if cheque is None:
                return None
            return self._to_dict(cheque)

    def update(self, cheque_id: str, updates: dict) -> None:
        with self._session_factory() as session:
            cheque = session.get(Cheque, cheque_id)
            if cheque is None:
                raise KeyError(cheque_id)
            self._apply_top_level(cheque, updates)
            for key, value in updates.items():
                if key in _KNOWN_TOP_LEVEL_KEYS and value is not None:
                    self._route_update(session, cheque, key, value)
            session.commit()

    def list_all(self) -> list[dict]:
        with self._session_factory() as session:
            cheques = session.query(Cheque).all()
            return [self._to_dict(c) for c in cheques]

    def clear_for_testing(self) -> None:
        """Real DELETEs (cascading via FK relationships), matching the
        in-memory repository's own test-only clear method so existing
        test fixtures work unchanged regardless of which backend is active."""
        with self._session_factory() as session:
            session.query(Cheque).delete()
            session.commit()

    # -- internal mapping -------------------------------------------------

    def _apply_top_level(self, cheque: Cheque, data: dict) -> None:
        extra = dict(cheque.upload_metadata or {})
        for key, value in data.items():
            if key in _KNOWN_TOP_LEVEL_KEYS or key == "cheque_id":
                continue
            if key == "processing_status":
                cheque.processing_status = value
            elif key == "file_hash":
                cheque.file_hash = value
            elif key == "file_type":
                cheque.file_type = value or cheque.file_type
            elif key == "file_name":
                cheque.image_path = value or cheque.image_path
            else:
                extra[key] = value
        cheque.upload_metadata = extra

    def _route_update(self, session: Session, cheque: Cheque, key: str, value: dict) -> None:
        handler = getattr(self, f"_apply_{key}", None)
        if handler is not None:
            handler(session, cheque, value)

    def _apply_extraction(self, session: Session, cheque: Cheque, extraction: dict) -> None:
        fields = extraction.get("fields", {})

        def _field(name):
            return fields.get(name, {}).get("value")

        cheque.cheque_number = _field("cheque_number")
        cheque.payee_name = _field("payee_name")
        amount = _field("amount")
        cheque.amount = amount if amount is not None else None
        cheque.cheque_date = _parse_date(_field("date"))
        cheque.routing_transit_number = _field("routing_transit_number")

        ocr_row = session.query(OCRResult).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if ocr_row is None:
            ocr_row = OCRResult(cheque_id=cheque.cheque_id, engine_name="Tesseract", status="SUCCESS")
            session.add(ocr_row)
        ocr_row.extracted_fields = fields
        merged = dict(ocr_row.full_result or {})
        merged["extraction"] = extraction
        ocr_row.full_result = merged

    def _apply_ocr(self, session: Session, cheque: Cheque, ocr: dict) -> None:
        ocr_row = session.query(OCRResult).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if ocr_row is None:
            ocr_row = OCRResult(cheque_id=cheque.cheque_id, engine_name=ocr.get("engine_name", "Tesseract"), status=ocr.get("ocr_status", "SUCCESS"))
            session.add(ocr_row)
        ocr_row.engine_name = ocr.get("engine_name", ocr_row.engine_name)
        ocr_row.engine_version = ocr.get("engine_version")
        ocr_row.raw_text = ocr.get("raw_text")
        ocr_row.confidence_score = ocr.get("average_confidence")
        ocr_row.processing_time_ms = int(ocr.get("processing_time_ms") or 0) or None
        ocr_row.status = ocr.get("ocr_status", ocr_row.status)
        ocr_row.error_message = ocr.get("error_message")
        merged = dict(ocr_row.full_result or {})
        merged["ocr"] = ocr
        ocr_row.full_result = merged

    def _apply_validation(self, session: Session, cheque: Cheque, validation: dict) -> None:
        checks = validation.get("checks", {})

        def _passed(name: str) -> bool:
            check = checks.get(name)
            return bool(check) and check.get("status") == "PASS"

        row = session.query(ValidationResult).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if row is None:
            row = ValidationResult(cheque_id=cheque.cheque_id, account_valid=False, cheque_number_valid=False, series_valid=False, routing_transit_number_valid=False, date_valid=False, overall_status="FAIL")
            session.add(row)
        row.account_valid = _passed("ACCOUNT_EXISTS") and _passed("ACCOUNT_STATUS")
        row.cheque_number_valid = checks.get("REQUIRED_FIELDS", {}).get("status") != "FAIL"
        row.series_valid = _passed("CHEQUE_SERIES")
        row.routing_transit_number_valid = _passed("ROUTING_TRANSIT")
        row.date_valid = _passed("DATE_WINDOW")
        row.payee_match = _passed("PAYEE_MATCH") if "PAYEE_MATCH" in checks else None
        row.amount_valid = _passed("AMOUNT") if "AMOUNT" in checks else None
        row.overall_status = validation.get("overall_validation_status", "FAIL")
        row.validation_message = validation.get("validation_message")
        row.checks = checks
        row.full_result = validation

    def _apply_fraud_analysis(self, session: Session, cheque: Cheque, fraud: dict) -> None:
        row = session.query(FraudResult).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if row is None:
            row = FraudResult(cheque_id=cheque.cheque_id, tampering_detected=False, fraud_score=0.0, fraud_level="LOW")
            session.add(row)
        image_analysis = fraud.get("image_analysis") or {}
        tampering_score = image_analysis.get("image_tampering_score")
        row.tampering_detected = bool(tampering_score and tampering_score >= 0.5)
        row.tampering_score = tampering_score
        row.fraud_score = fraud.get("fraud_risk_score", 0.0)
        row.fraud_level = fraud.get("risk_level", "LOW")
        row.indicators = fraud.get("indicators")
        row.model_name = "fraud-detection-engine"
        row.model_version = fraud.get("engine_version")
        row.full_result = fraud

        duplicate_analysis = fraud.get("duplicate_analysis") or {}
        dup_row = session.query(DuplicateResult).filter_by(cheque_id=cheque.cheque_id).order_by(DuplicateResult.created_at.desc()).first()
        if dup_row is None:
            dup_row = DuplicateResult(cheque_id=cheque.cheque_id, duplicate_detected=False)
            session.add(dup_row)
        dup_row.duplicate_detected = duplicate_analysis.get("duplicate_status") == "CONFIRMED_DUPLICATE"
        dup_row.matched_cheque_id = duplicate_analysis.get("matched_cheque_id")
        dup_row.similarity_score = duplicate_analysis.get("perceptual_similarity")
        dup_row.comparison_method = "multi-level (data/hash/perceptual)"
        dup_row.full_result = duplicate_analysis

    def _apply_signature_analysis(self, session: Session, cheque: Cheque, signature: dict) -> None:
        row = session.query(SignatureResult).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if row is None:
            row = SignatureResult(cheque_id=cheque.cheque_id, status="UNCERTAIN")
            session.add(row)
        similarity = signature.get("similarity_score")
        row.similarity_score = (similarity * 100) if similarity is not None else None
        risk_level = signature.get("risk_level")
        row.status = {"LOW": "MATCH", "MEDIUM": "UNCERTAIN", "HIGH": "MISMATCH", "CRITICAL": "MISMATCH", "UNAVAILABLE": "UNCERTAIN"}.get(risk_level, "UNCERTAIN")
        row.model_name = signature.get("model_name")
        row.model_version = signature.get("model_version")
        row.full_result = signature

    def _apply_anomaly_analysis(self, session: Session, cheque: Cheque, anomaly: dict) -> None:
        row = session.query(AnomalyResult).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if row is None:
            row = AnomalyResult(cheque_id=cheque.cheque_id, anomaly_score=0.0, anomaly_level="LOW")
            session.add(row)
        row.anomaly_score = anomaly.get("anomaly_score", 0.0)
        row.anomaly_level = anomaly.get("risk_level", "LOW")
        row.detected_patterns = anomaly.get("anomalies")
        row.model_name = anomaly.get("model_name")
        row.model_version = anomaly.get("model_version")
        row.full_result = anomaly

    def _apply_risk_assessment(self, session: Session, cheque: Cheque, risk: dict) -> None:
        row = session.query(RiskAssessment).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if row is None:
            row = RiskAssessment(cheque_id=cheque.cheque_id, overall_risk_score=0.0, risk_level="LOW")
            session.add(row)
        factor_by_name = {f["factor"]: f["contribution"] for f in risk.get("risk_factors", [])}
        row.fraud_score = factor_by_name.get("TAMPERING")
        row.validation_score = factor_by_name.get("VALIDATION")
        row.signature_score = factor_by_name.get("SIGNATURE")
        row.duplicate_score = factor_by_name.get("DUPLICATE")
        row.anomaly_score = factor_by_name.get("ANOMALY")
        row.overall_risk_score = risk.get("overall_risk_score", 0.0)
        row.risk_level = risk.get("risk_level", "LOW")
        row.risk_factors = risk.get("risk_factors")
        row.model_version = risk.get("config_version")
        row.full_result = risk

    def _apply_decision(self, session: Session, cheque: Cheque, decision: dict) -> None:
        row = session.query(Decision).filter_by(cheque_id=cheque.cheque_id).one_or_none()
        if row is None:
            row = Decision(cheque_id=cheque.cheque_id, decision="REVIEW", risk_score=0.0, risk_level="LOW", reason="", review_required=True)
            session.add(row)
        row.decision = decision.get("decision", "REVIEW")
        row.risk_score = decision.get("risk_score", 0.0)
        row.risk_level = decision.get("risk_level", "LOW")
        row.decision_rule = (decision.get("triggered_rules") or [None])[0]
        row.reason = decision.get("decision_reason", "")
        row.review_required = decision.get("requires_manual_review", False)
        row.engine_version = decision.get("ruleset_version")
        row.triggered_rules = decision.get("triggered_rules")
        row.reasons = decision.get("reasons")
        row.full_result = decision

    # -- reconstruction ---------------------------------------------------

    def _to_dict(self, cheque: Cheque) -> dict:
        record: dict = {
            "cheque_id": cheque.cheque_id,
            "processing_status": cheque.processing_status,
            "file_hash": cheque.file_hash,
            "file_type": cheque.file_type,
            "file_name": cheque.image_path,
            **(cheque.upload_metadata or {}),
        }
        if cheque.ocr_result is not None:
            full = cheque.ocr_result.full_result or {}
            record["ocr"] = full.get("ocr")
            record["extraction"] = full.get("extraction")
        if cheque.validation_result is not None:
            record["validation"] = cheque.validation_result.full_result
        if cheque.fraud_result is not None:
            record["fraud_analysis"] = cheque.fraud_result.full_result
        if cheque.signature_result is not None:
            record["signature_analysis"] = cheque.signature_result.full_result
        if cheque.anomaly_result is not None:
            record["anomaly_analysis"] = cheque.anomaly_result.full_result
        if cheque.risk_assessment is not None:
            record["risk_assessment"] = cheque.risk_assessment.full_result
        if cheque.decision is not None:
            record["decision"] = cheque.decision.full_result
        return record
