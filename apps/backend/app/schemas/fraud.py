from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FraudIndicatorResponse(BaseModel):
    type: str
    severity: str
    reason: str
    contribution: float
    evidence: dict[str, Any] | None = None


class RuleViolationResponse(BaseModel):
    rule_id: str
    description: str
    triggered_by: list[str]


class FraudAnalysisResponse(BaseModel):
    """docs/26_API_Specification.md S15-S16, extended with the structured,
    per-indicator evidence and rule-violation detail this milestone's
    "explainable fraud detection" requirement calls for (docs/17 S23-S24)
    -- docs/26's own example (`fraud_score`, `fraud_level`, a flat
    boolean `indicators` object) is a minimal illustration; the richer
    structure here supersedes it, consistent with how Milestones 3 and 4
    extended the OCR and validation result endpoints. `tampering_detected`
    is kept as a literal boolean for docs/26 compatibility alongside the
    richer `image_analysis` block."""

    cheque_id: str
    fraud_risk_score: float
    risk_level: str
    tampering_detected: bool
    model_prediction: str
    indicators: list[FraudIndicatorResponse]
    rule_violations: list[RuleViolationResponse]
    explanation: list[str]
    confidence: float
    analysis_timestamp: str
    engine_version: str
    recommendation: str
    unavailable_inputs: list[str]
    duplicate_analysis: dict[str, Any]
    image_analysis: dict[str, Any]
