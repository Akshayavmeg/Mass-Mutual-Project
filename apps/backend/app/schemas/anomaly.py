from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AnomalyItemResponse(BaseModel):
    type: str
    severity: str
    reason: str
    contribution: float
    evidence: dict[str, Any] | None = None


class AnomalyAnalysisResponse(BaseModel):
    """docs/26_API_Specification.md S19, extended with the structured
    per-anomaly evidence docs/20_Anomaly_Detection.md S30 requires."""

    cheque_id: str
    account_number: str | None
    anomaly_score: float
    risk_level: str
    anomalies: list[AnomalyItemResponse]
    reasons: list[str]
    model_name: str
    model_version: str
    analysis_timestamp: str
    analysis_status: str
    unavailable_inputs: list[str]
