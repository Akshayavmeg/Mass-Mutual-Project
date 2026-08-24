"""Structured decision result (docs/22_Decision_Engine.md S17).

Module boundary: this is the first milestone allowed to produce
APPROVE/REVIEW/REJECT -- but it never performs OCR, validation, fraud
detection, signature analysis, anomaly detection, or risk scoring
itself; it only reads their already-persisted results (docs/22 S1: "the
bridge between the analytical modules and the final cheque-processing
workflow").
"""

from __future__ import annotations

from dataclasses import dataclass, field

DECISIONS = ("APPROVE", "REVIEW", "REJECT")


@dataclass
class DecisionResult:
    cheque_id: str
    decision: str  # one of DECISIONS
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
    evidence: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "reasons": self.reasons,
            "triggered_rules": self.triggered_rules,
            "risk_score": round(self.risk_score, 2),
            "risk_level": self.risk_level,
            "requires_manual_review": self.requires_manual_review,
            "escalation_reason": self.escalation_reason,
            "unavailable_inputs": self.unavailable_inputs,
            "ruleset_version": self.ruleset_version,
            "policy_version": self.policy_version,
            "decision_timestamp": self.decision_timestamp,
            "evidence": self.evidence,
        }
