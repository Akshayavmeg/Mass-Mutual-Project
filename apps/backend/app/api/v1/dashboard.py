"""Dashboard API (docs/26_API_Specification.md S27-S29). See
app/services/dashboard/dashboard_service.py's module docstring for why
these endpoints -- documented in docs/26 but not built by any earlier
milestone -- are added here as this milestone's authorized gap-fill.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.authorization import Permission, require_permission
from app.schemas.dashboard import DashboardSummaryResponse, FraudStatisticsResponse, ProcessingStatisticsResponse
from app.services.dashboard import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(_role=Depends(require_permission(Permission.CHEQUE_VIEW))):
    return DashboardSummaryResponse(**dashboard_service.get_summary())


@router.get("/fraud-statistics", response_model=FraudStatisticsResponse)
async def get_fraud_statistics(_role=Depends(require_permission(Permission.CHEQUE_VIEW))):
    return FraudStatisticsResponse(**dashboard_service.get_fraud_statistics())


@router.get("/processing-statistics", response_model=ProcessingStatisticsResponse)
async def get_processing_statistics(_role=Depends(require_permission(Permission.CHEQUE_VIEW))):
    return ProcessingStatisticsResponse(**dashboard_service.get_processing_statistics())
