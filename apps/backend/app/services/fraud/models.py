"""Structured fraud-detection result types (docs/17_Fraud_Detection.md
S23-S24, S30).

Module boundary (docs/17 S42, S31): this is EVIDENCE for the Risk
Scoring and Decision Engine modules (Milestones 6/7) -- the Fraud
Detection Engine does not itself approve/reject a cheque.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


@dataclass(frozen=True)
class FraudIndicator:
    """One explainable piece of fraud evidence (docs/17 S23: never just
    `Fraud = TRUE` -- every indicator names its type, severity, and the
    reason/evidence behind it)."""

    type: str
    severity: str  # one of SEVERITIES
    reason: str
    contribution: float  # points this indicator adds to fraud_risk_score
    evidence: dict[str, Any] | None = None

    def as_dict(self) -> dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "reason": self.reason,
            "contribution": round(self.contribution, 2),
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class RuleViolation:
    rule_id: str
    description: str
    triggered_by: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"rule_id": self.rule_id, "description": self.description, "triggered_by": self.triggered_by}


@dataclass
class FraudResult:
    cheque_id: str
    fraud_risk_score: float
    risk_level: str
    model_prediction: str
    indicators: list[FraudIndicator]
    rule_violations: list[RuleViolation]
    confidence: float
    analysis_timestamp: str
    engine_version: str
    recommendation: str
    unavailable_inputs: list[str] = field(default_factory=list)

    @property
    def explanation(self) -> list[str]:
        return [ind.reason for ind in self.indicators]

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "fraud_risk_score": round(self.fraud_risk_score, 2),
            "risk_level": self.risk_level,
            "model_prediction": self.model_prediction,
            "indicators": [ind.as_dict() for ind in self.indicators],
            "rule_violations": [rv.as_dict() for rv in self.rule_violations],
            "explanation": self.explanation,
            "confidence": round(self.confidence, 2),
            "analysis_timestamp": self.analysis_timestamp,
            "engine_version": self.engine_version,
            "recommendation": self.recommendation,
            "unavailable_inputs": self.unavailable_inputs,
        }


def classify_risk_level(score: float, bands: dict[str, list[int]]) -> str:
    for level in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        low, high = bands[level]
        if low <= score <= high:
            return level
    return "CRITICAL" if score > 100 else "LOW"
