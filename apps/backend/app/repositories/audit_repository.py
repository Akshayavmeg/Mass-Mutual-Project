"""Audit log repository (Milestone 8; docs/27_Audit_Trail.md,
docs/25_Database_Schema.md S18).

Append-only from the application's perspective (docs/27 S "audit
records must remain append-only"): no `update`/`delete` method is
exposed, only `record` and read methods.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Protocol


class AuditLogRepository(Protocol):
    def record(self, event: dict) -> dict: ...

    def list_for_cheque(self, cheque_id: str) -> list[dict]: ...

    def list_all(self, *, limit: int = 100) -> list[dict]: ...


class InMemoryAuditLogRepository:
    """Fallback used when no reachable PostgreSQL is configured (see
    app.repositories.db_availability) -- append-only in-process list,
    matching the same test/dev-adapter pattern as the other Milestone
    3-7 in-memory repositories."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: list[dict] = []

    def record(self, event: dict) -> dict:
        stored = dict(event)
        stored.setdefault("audit_id", str(uuid.uuid4()))
        stored.setdefault("event_timestamp", datetime.now(timezone.utc).isoformat())
        with self._lock:
            self._events.append(stored)
        return stored

    def list_for_cheque(self, cheque_id: str) -> list[dict]:
        with self._lock:
            return [e for e in self._events if e.get("cheque_id") == cheque_id]

    def list_all(self, *, limit: int = 100) -> list[dict]:
        with self._lock:
            return list(self._events[-limit:])

    def clear_for_testing(self) -> None:
        with self._lock:
            self._events.clear()


_repository = InMemoryAuditLogRepository()
_postgres_repository = None


def get_audit_repository() -> AuditLogRepository:
    global _postgres_repository
    from app.repositories.db_availability import postgres_available

    if postgres_available():
        if _postgres_repository is None:
            from app.repositories.postgres_audit_repository import PostgresAuditLogRepository

            _postgres_repository = PostgresAuditLogRepository()
        return _postgres_repository
    return _repository
