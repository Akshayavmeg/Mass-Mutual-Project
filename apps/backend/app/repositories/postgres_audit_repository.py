"""PostgreSQL-backed AuditLogRepository (Milestone 8; docs/27_Audit_Trail.md
S13 canonical `audit_logs` schema)."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session, sessionmaker

from app.core.database import SessionLocal
from app.models.audit import AuditLog


def _to_dict(row: AuditLog) -> dict:
    return {
        "audit_id": str(row.audit_id),
        "cheque_id": row.cheque_id,
        "event_type": row.event_type,
        "event_timestamp": row.event_timestamp.isoformat() if row.event_timestamp else None,
        "user_id": row.user_id,
        "user_role": row.user_role,
        "source": row.source,
        "previous_status": row.previous_status,
        "new_status": row.new_status,
        "action": row.action,
        "result": row.result,
        "reason": row.reason,
        "request_id": row.request_id,
        "ip_address": row.ip_address,
        "metadata": row.event_metadata,
    }


class PostgresAuditLogRepository:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    def record(self, event: dict) -> dict:
        with self._session_factory() as session:
            row = AuditLog(
                audit_id=uuid.uuid4(),
                cheque_id=event.get("cheque_id"),
                event_type=event["event_type"],
                user_id=event.get("user_id"),
                user_role=event.get("user_role"),
                source=event.get("source", "SYSTEM"),
                previous_status=event.get("previous_status"),
                new_status=event.get("new_status"),
                action=event.get("action"),
                result=event.get("result"),
                reason=event.get("reason"),
                request_id=event.get("request_id"),
                ip_address=event.get("ip_address"),
                event_metadata=event.get("metadata"),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_dict(row)

    def list_for_cheque(self, cheque_id: str) -> list[dict]:
        with self._session_factory() as session:
            rows = session.query(AuditLog).filter_by(cheque_id=cheque_id).order_by(AuditLog.event_timestamp).all()
            return [_to_dict(r) for r in rows]

    def list_all(self, *, limit: int = 100) -> list[dict]:
        with self._session_factory() as session:
            rows = session.query(AuditLog).order_by(AuditLog.event_timestamp.desc()).limit(limit).all()
            return [_to_dict(r) for r in rows]
