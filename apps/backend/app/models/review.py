"""User and Manual Review Case ORM models (docs/25_Database_Schema.md
S16-S17).

Reviewer comments (docs/23_Manual_Review_Workflow.md S14) are stored as
a JSONB list on `manual_review_cases` rather than a separate table --
docs/25 does not document a distinct comments table, and ADR-0003
specifically names JSONB as the mechanism for this kind of
semi-structured, per-record list.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ManualReviewCase(Base):
    __tablename__ = "manual_review_cases"
    __table_args__ = (
        CheckConstraint("reviewer_decision IS NULL OR reviewer_decision IN ('APPROVE','REJECT')", name="chk_reviewer_decision_value"),
    )

    review_case_id: Mapped[str] = mapped_column(String(50), primary_key=True)  # REV-YYYY-NNNNNN format
    cheque_id: Mapped[str] = mapped_column(String(50), ForeignKey("cheques.cheque_id"), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    trigger_reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    assigned_reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True, index=True)
    reviewer_decision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reviewer_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comments: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    automated_decision: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Full snapshot (cheque_summary, validation/fraud/signature/anomaly/
    # risk evidence) for exact round-trip with the existing review_service
    # dict shape -- see processing_results.py's module docstring for the
    # same full_result rationale.
    full_case: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    cheque: Mapped["Cheque"] = relationship(back_populates="manual_review_cases")  # noqa: F821
