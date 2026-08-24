"""Structured anomaly-detection result (docs/20_Anomaly_Detection.md
S30).

Module boundary (docs/20 S1, S32): an anomaly is not automatically
fraud -- this module produces evidence and a score for the Fraud
Detection/Risk Scoring stages, never a fraud verdict itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AnomalyItem:
    type: str
    severity: str  # "MODERATE" | "HIGH" | "CRITICAL" (docs/20 S11 Z-score bands) or "MEDIUM" for non-Z-score types
    reason: str
    contribution: float
    evidence: dict[str, Any] | None = None

    def as_dict(self) -> dict:
        return {
            "type": self.type, "severity": self.severity, "reason": self.reason,
            "contribution": round(self.contribution, 2), "evidence": self.evidence,
        }


@dataclass
class AnomalyResult:
    cheque_id: str
    account_number: str | None
    anomaly_score: float
    risk_level: str
    anomalies: list[AnomalyItem]
    model_name: str
    model_version: str
    analysis_timestamp: str
    analysis_status: str
    unavailable_inputs: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "account_number": self.account_number,
            "anomaly_score": round(self.anomaly_score, 2),
            "risk_level": self.risk_level,
            "anomalies": [a.as_dict() for a in self.anomalies],
            "reasons": [a.reason for a in self.anomalies],
            "model_name": self.model_name,
            "model_version": self.model_version,
            "analysis_timestamp": self.analysis_timestamp,
            "analysis_status": self.analysis_status,
            "unavailable_inputs": self.unavailable_inputs,
        }
