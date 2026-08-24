from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class DecisionResponse(BaseModel):
    """docs/26_API_Specification.md S21-S22, extended with the full
    explainable structure docs/22_Decision_Engine.md S17 requires
    (triggered_rules, escalation_reason, unavailable_inputs, policy
    version) -- consistent with how Milestones 3-6 extended their own
    flat docs/26 examples."""

    cheque_id: str
    decision: str
    decision_reason: str
    reasons: list[str]
    triggered_rules: list[str]
    risk_score: float
    risk_level: str
    requires_manual_review: bool
    escalation_reason: str | None
    unavailable_inputs: list[str]
    ruleset_version: str
    policy_version: str
    decision_timestamp: str
    evidence: dict[str, Any]
