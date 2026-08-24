from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Health check endpoint (docs/26_API_Specification.md Section 32).

    Never fails outright: an unreachable database is reported via the
    `database` field rather than raising, so the endpoint stays usable for
    liveness checks even when a dependency is degraded.
    """
    database_status = "connected" if check_database_connection() else "disconnected"
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        database=database_status,
    )
