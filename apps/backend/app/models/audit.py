"""`audit_logs` ORM model -- canonical schema per docs/27_Audit_Trail.md
S13 (reproduced in docs/25_Database_Schema.md S18, docs/24 S22)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cheque_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(30), nullable=False)  # SYSTEM / USER / API
    previous_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    # Python attribute is `event_metadata` ("metadata" is reserved by
    # SQLAlchemy's DeclarativeBase for the schema registry), but the
    # actual database column is named "metadata" per docs/27 S13's
    # canonical field name.
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
