from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RiskFactorResponse(BaseModel):
    factor: str
    contribution: float
    max_contribution: float
    reason: str
    evidence: dict[str, Any] | None = None


class RiskScoreResponse(BaseModel):
    """docs/26_API_Specification.md S20, extended with the full
    contributing-factor breakdown docs/21_Risk_Scoring.md S19 requires
    for explainability -- docs/26's own flat `components` example is
    superseded by the richer `risk_factors` structure here, consistent
    with the precedent set by Milestones 3-5."""

    cheque_id: str
    overall_risk_score: float
    risk_level: str
    risk_factors: list[RiskFactorResponse]
    hard_rules_triggered: list[str]
    unavailable_inputs: list[str]
    config_version: str
    analysis_timestamp: str
