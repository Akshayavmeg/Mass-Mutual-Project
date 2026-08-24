"""SQLAlchemy engine/session setup.

Per ADR-0003, PostgreSQL is accessed through SQLAlchemy from the backend
service layer only -- the frontend never connects to the database directly.

No models exist yet: ORM models, repositories, and Alembic migrations are
introduced in Milestone 8 (Database, API & Audit Trail) once the schema in
docs/25_Database_Schema.md is implemented. This module only establishes the
connection/session foundation so later milestones have somewhere to plug in.
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
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base for future ORM models (Milestone 8)."""


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
