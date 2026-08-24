"""SQLAlchemy engine/session setup (Milestone 8; docs/25_Database_Schema.md,
ADR-0003).

Per ADR-0003, PostgreSQL is accessed through SQLAlchemy from the backend
service layer only -- the frontend never connects to the database directly.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# pool_pre_ping avoids handing out stale/dead connections; the engine itself
# does not connect eagerly, so importing this module works even if the
# database is not currently reachable (fail-safe: only actual DB use fails).
# connect_timeout bounds how long any single connection attempt can take, so
# a missing/unreachable database degrades quickly (e.g. for the health
# check) instead of hanging the request.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout_seconds,
    connect_args={"connect_timeout": settings.database_connect_timeout_seconds},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base for all ORM models (app/models/)."""


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Best-effort connectivity check used by the health endpoint.

    Never raises: a failed check is reported as unavailable rather than
    crashing the request, consistent with the project's fail-safe principle
    (docs/08_System_Architecture.md Section 21).
    """
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 - deliberately broad for a health probe
        return False
