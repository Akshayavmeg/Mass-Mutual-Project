"""Structured overall risk-assessment result (docs/21_Risk_Scoring.md
S19-S20).

Module boundary (docs/21 S1, S30): the risk score is decision-SUPPORT
for the Decision Engine (Milestone 7) -- this module never itself
approves, reviews, or rejects a cheque.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RiskFactor:
    factor: str
    contribution: float
    max_contribution: float
    reason: str
    evidence: dict[str, Any] | None = None

    def as_dict(self) -> dict:
        return {
            "factor": self.factor, "contribution": round(self.contribution, 2),
            "max_contribution": self.max_contribution, "reason": self.reason, "evidence": self.evidence,
        }


@dataclass
class RiskAssessmentResult:
    cheque_id: str
    overall_risk_score: float
    risk_level: str
    risk_factors: list[RiskFactor]
    hard_rules_triggered: list[str]
    unavailable_inputs: list[str]
    config_version: str
    analysis_timestamp: str

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "overall_risk_score": round(self.overall_risk_score, 2),
            "risk_level": self.risk_level,
            "risk_factors": [f.as_dict() for f in self.risk_factors],
            "hard_rules_triggered": self.hard_rules_triggered,
            "unavailable_inputs": self.unavailable_inputs,
            "config_version": self.config_version,
            "analysis_timestamp": self.analysis_timestamp,
        }
