"""Shared, memoized PostgreSQL-reachability check used by every
repository factory (Milestone 8).

`settings.use_postgres_repositories` selects PostgreSQL as the intended
production backend (ADR-0003); this module additionally verifies the
database is actually reachable before committing to it, so environments
without a live PostgreSQL server (this development environment
included -- see the Milestone 8 report) transparently fall back to the
existing Milestone 3-7 in-memory/CSV repositories rather than every
request failing. This is an explicit, documented fallback, not a
silent substitute production database (no SQLite is ever used).
"""

from __future__ import annotations

from app.core.config import settings
from app.core.database import check_database_connection

_cached: bool | None = None


def postgres_available() -> bool:
    global _cached
    if _cached is None:
        _cached = settings.use_postgres_repositories and check_database_connection()
    return _cached


def reset_for_testing() -> None:
    global _cached
    _cached = None
