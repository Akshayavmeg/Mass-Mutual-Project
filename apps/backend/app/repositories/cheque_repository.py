"""Cheque processing-record repository.

Milestone 8 (Database, API & Audit Trail) implements the real
PostgreSQL-backed repository per docs/25_Database_Schema.md. Milestones
0-7 do not build the database layer yet, so this module provides an
in-memory implementation behind the same simple interface, which lets the
API and service layers be written once and keep working unchanged once a
persistent repository is substituted (NFR-006: database implementations
must be independently modifiable).

This is explicitly NOT a production persistence mechanism: records do not
survive a process restart, and there is no cross-process sharing. That is
an accepted, documented limitation of this milestone, not a hidden one.
"""

from __future__ import annotations

import threading
from typing import Protocol


class ChequeRecordRepository(Protocol):
    def save(self, cheque_id: str, record: dict) -> None: ...

    def get(self, cheque_id: str) -> dict | None: ...

    def update(self, cheque_id: str, updates: dict) -> None: ...

    def list_all(self) -> list[dict]: ...


class InMemoryChequeRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, dict] = {}

    def save(self, cheque_id: str, record: dict) -> None:
        with self._lock:
            self._records[cheque_id] = dict(record)

    def get(self, cheque_id: str) -> dict | None:
        with self._lock:
            record = self._records.get(cheque_id)
            return dict(record) if record is not None else None

    def update(self, cheque_id: str, updates: dict) -> None:
        with self._lock:
            if cheque_id not in self._records:
                raise KeyError(cheque_id)
            self._records[cheque_id].update(updates)

    def list_all(self) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self._records.values()]

    def clear_for_testing(self) -> None:
        with self._lock:
            self._records.clear()


_repository = InMemoryChequeRepository()


def get_cheque_repository() -> InMemoryChequeRepository:
    return _repository
