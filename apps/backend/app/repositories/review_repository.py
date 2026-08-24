"""Manual-review-case repository (docs/23_Manual_Review_Workflow.md
S23).

Mirrors app/repositories/cheque_repository.py's in-memory placeholder
pattern exactly (ADR explicitly documented there): Milestone 8 will
substitute a PostgreSQL-backed implementation behind this same simple
interface without any Decision Engine/review-service code changing
(NFR-006).
"""

from __future__ import annotations

import threading
from typing import Protocol


class ReviewCaseRepository(Protocol):
    def save(self, review_case_id: str, record: dict) -> None: ...

    def get(self, review_case_id: str) -> dict | None: ...

    def update(self, review_case_id: str, updates: dict) -> None: ...

    def list_all(self) -> list[dict]: ...

    def get_by_cheque_id(self, cheque_id: str) -> dict | None: ...


class InMemoryReviewCaseRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cases: dict[str, dict] = {}

    def save(self, review_case_id: str, record: dict) -> None:
        with self._lock:
            self._cases[review_case_id] = dict(record)

    def get(self, review_case_id: str) -> dict | None:
        with self._lock:
            record = self._cases.get(review_case_id)
            return dict(record) if record is not None else None

    def update(self, review_case_id: str, updates: dict) -> None:
        with self._lock:
            if review_case_id not in self._cases:
                raise KeyError(review_case_id)
            self._cases[review_case_id].update(updates)

    def list_all(self) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self._cases.values()]

    def get_by_cheque_id(self, cheque_id: str) -> dict | None:
        with self._lock:
            for record in self._cases.values():
                if record["cheque_id"] == cheque_id:
                    return dict(record)
            return None

    def clear_for_testing(self) -> None:
        with self._lock:
            self._cases.clear()


_repository = InMemoryReviewCaseRepository()


def get_review_repository() -> InMemoryReviewCaseRepository:
    return _repository
