"""`cheques` table -- the central table of the schema (docs/25_Database_Schema.md S7)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

PROCESSING_STATUSES = (
    "UPLOADED", "PROCESSING", "OCR_COMPLETED", "VALIDATED", "FRAUD_ANALYZED",
    "SIGNATURE_ANALYZED", "ANOMALY_ANALYZED", "RISK_SCORED", "DECISION_MADE",
    "UNDER_REVIEW", "APPROVED", "UNDER_REVIEW_CLOSED", "REJECTED", "FAILED",
)


class Cheque(Base):
    __tablename__ = "cheques"
    __table_args__ = (
        CheckConstraint("amount IS NULL OR amount >= 0", name="chk_cheque_amount_non_negative"),
    )

    cheque_id: Mapped[str] = mapped_column(String(50), primary_key=True)  # Processing ID format CHK-YYYY-NNNNNN
    account_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_accounts.account_id"), nullable=True)
    cheque_number: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    cheque_series: Mapped[str | None] = mapped_column(String(30), nullable=True)
    routing_transit_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payee_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cheque_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False, index=True, default="UPLOADED")
    # Upload metadata (original filename, dimensions, preprocessing
    # result, human_decision, etc.) not broken out into their own
    # documented columns/tables -- see the Milestone 8 report.
    upload_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    account: Mapped["BankAccount | None"] = relationship(back_populates="cheques")  # noqa: F821
    ocr_result: Mapped["OCRResult | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    validation_result: Mapped["ValidationResult | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    fraud_result: Mapped["FraudResult | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    signature_result: Mapped["SignatureResult | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    duplicate_result: Mapped["DuplicateResult | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan", foreign_keys="[DuplicateResult.cheque_id]")  # noqa: F821
    anomaly_result: Mapped["AnomalyResult | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    risk_assessment: Mapped["RiskAssessment | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    decision: Mapped["Decision | None"] = relationship(back_populates="cheque", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    manual_review_cases: Mapped[list["ManualReviewCase"]] = relationship(back_populates="cheque", cascade="all, delete-orphan")  # noqa: F821
