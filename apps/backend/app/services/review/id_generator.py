"""Review case ID generation (docs/23_Manual_Review_Workflow.md S6
example: REV-2026-000045). Mirrors
app/services/cheque/id_generator.py's thread-safe in-process counter
pattern exactly."""

from __future__ import annotations

import threading
from datetime import datetime, timezone

_lock = threading.Lock()
_counters: dict[int, int] = {}


def generate_review_case_id(*, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    year = now.year
    with _lock:
        _counters[year] = _counters.get(year, 0) + 1
        sequence = _counters[year]
    return f"REV-{year}-{sequence:06d}"


def reset_counters_for_testing() -> None:
    with _lock:
        _counters.clear()
