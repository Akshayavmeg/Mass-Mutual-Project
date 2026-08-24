"""Per-cheque processing-result ORM models (docs/25_Database_Schema.md
S8-S15, S18-S19), each in a 1:1 (or documented 1:N for duplicate)
relationship with `cheques`.

Each table has the documented typed columns (for indexing/querying, per
docs/25's own indexing strategy) PLUS a `full_result` JSONB column
holding the complete, already-computed Milestone 4-7 result dict
verbatim. This is deliberate: it lets the Postgres-backed repositories
round-trip the exact nested dict shape the existing M3-7 service layer
already produces/consumes (this milestone's "repository interfaces must
remain stable" requirement) without requiring this milestone to
decompose every nested indicator/evidence field into its own typed
column -- while the individually-typed columns docs/25 documents are
still populated and remain independently queryable. JSONB was
specifically named in ADR-0003 as the mechanism for this kind of
semi-structured storage.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OCRResult(Base):
    __tablename__ = "ocr_results"

    ocr_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    engine_name: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Milestone 3 canonical field dict
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # complete ocr+extraction dict
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="ocr_result")  # noqa: F821


class ValidationResult(Base):
    __tablename__ = "validation_results"
    __table_args__ = (
        CheckConstraint("overall_status IN ('PASS','FAIL','WARNING')", name="chk_validation_overall_status"),
    )

    validation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    account_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cheque_number_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    series_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    routing_transit_number_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    payee_match: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    amount_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    overall_status: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    checks: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Milestone 4's full per-check breakdown
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="validation_result")  # noqa: F821


class FraudResult(Base):
    __tablename__ = "fraud_results"
    __table_args__ = (
        CheckConstraint("fraud_score >= 0 AND fraud_score <= 100", name="chk_fraud_score_range"),
    )

    fraud_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    tampering_detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tampering_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    fraud_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    fraud_level: Mapped[str] = mapped_column(String(20), nullable=False)
    indicators: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="fraud_result")  # noqa: F821


class SignatureResult(Base):
    __tablename__ = "signature_results"
    __table_args__ = (
        CheckConstraint("similarity_score IS NULL OR (similarity_score >= 0 AND similarity_score <= 100)", name="chk_signature_similarity_range"),
    )

    signature_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    similarity_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="signature_result")  # noqa: F821


class DuplicateResult(Base):
    __tablename__ = "duplicate_results"

    duplicate_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), nullable=False, index=True)
    duplicate_detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    matched_cheque_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    comparison_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="duplicate_result", foreign_keys=[cheque_id])  # noqa: F821


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    anomaly_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    anomaly_level: Mapped[str] = mapped_column(String(20), nullable=False)
    detected_patterns: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="anomaly_result")  # noqa: F821


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    __table_args__ = (
        CheckConstraint("overall_risk_score >= 0 AND overall_risk_score <= 100", name="chk_risk_score_range"),
    )

    risk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    fraud_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    validation_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    signature_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    duplicate_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    anomaly_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    overall_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_factors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="risk_assessment")  # noqa: F821


class Decision(Base):
    __tablename__ = "decisions"
    __table_args__ = (
        CheckConstraint("decision IN ('APPROVE','REVIEW','REJECT')", name="chk_decision_value"),
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), unique=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    decision_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    triggered_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reasons: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="decision")  # noqa: F821
