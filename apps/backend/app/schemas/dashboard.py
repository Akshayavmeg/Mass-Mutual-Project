from __future__ import annotations

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    """docs/26_API_Specification.md S27 (GET /dashboard/summary)."""

    total_cheques: int
    approved: int
    under_review: int
    rejected: int
    fraud_detected: int
    average_processing_time_seconds: float | None
    average_ocr_confidence: float | None


class FraudStatisticsResponse(BaseModel):
    """docs/26_API_Specification.md S28 (GET /dashboard/fraud-statistics)."""

    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int


class ProcessingStatisticsResponse(BaseModel):
    """docs/26_API_Specification.md S29 (GET /dashboard/processing-statistics)."""

    average_processing_time: float | None
    ocr_success_rate: float | None
    validation_success_rate: float | None
    manual_review_rate: float | None
