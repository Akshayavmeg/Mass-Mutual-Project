"""Processing ID generation (docs/12_Cheque_Input_Module.md S10).

Format: CHK-<year>-<6-digit sequence>, e.g. CHK-2026-000001. Thread-safe
in-process counter; Milestone 8 can replace this with a database sequence
without changing the format or the callers.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone

_lock = threading.Lock()
_counters: dict[int, int] = {}


def generate_processing_id(*, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    year = now.year
    with _lock:
        _counters[year] = _counters.get(year, 0) + 1
        sequence = _counters[year]
    return f"CHK-{year}-{sequence:06d}"


def reset_counters_for_testing() -> None:
    """Test-only helper to make Processing ID sequences reproducible
    across test runs."""
    with _lock:
        _counters.clear()
