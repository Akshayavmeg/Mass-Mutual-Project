from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import cheques, dashboard, health, reviews, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(cheques.router, tags=["cheques"])
api_router.include_router(reviews.router, tags=["reviews"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(users.router, tags=["users"])
