from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.v1 import health
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s (environment=%s)", settings.app_name, settings.environment)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # /health is intentionally exposed outside the /api/v1 prefix too (see
    # docs/26_API_Specification.md Section 42); every other endpoint is
    # only mounted under settings.api_v1_prefix.
    app.include_router(health.router, tags=["health"])
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
