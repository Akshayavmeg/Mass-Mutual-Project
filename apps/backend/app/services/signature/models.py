"""Structured signature-analysis result (docs/18_Signature_Analysis.md
S23).

Module boundary (docs/18 S40): a signature mismatch is evidence for the
Fraud Detection Engine, never a fraud verdict by itself (docs/18 S17).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

INDICATORS = (
    None, "SIGNATURE_MISSING", "SIGNATURE_MISMATCH", "SIGNATURE_ANALYSIS_UNRELIABLE",
    "INSUFFICIENT_IMAGE", "SIGNATURE_IMAGE_LOW_QUALITY", "REFERENCE_SIGNATURE_NOT_FOUND",
    "SIGNATURE_ANALYSIS_ERROR", "UNSUPPORTED_SIGNATURE_IMAGE",
)


@dataclass
class SignatureAnalysisResult:
    cheque_id: str
    account_number: str | None
    signature_present: bool
    image_quality: str  # "GOOD" | "POOR" | "UNKNOWN"
    similarity_score: float | None
    analysis_confidence: float
    signature_tampering_score: float | None
    risk_level: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | "UNAVAILABLE"
    indicator: str | None
    recommendation: str
    analysis_status: str  # "COMPLETED" | "INSUFFICIENT_IMAGE" | "REFERENCE_SIGNATURE_NOT_FOUND" | "ERROR"
    model_name: str
    model_version: str
    analysis_timestamp: str
    reference_matches: list[dict] = field(default_factory=list)
    evidence: dict[str, Any] | None = None

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "account_number": self.account_number,
            "signature_present": self.signature_present,
            "image_quality": self.image_quality,
            "similarity_score": round(self.similarity_score, 4) if self.similarity_score is not None else None,
            "analysis_confidence": round(self.analysis_confidence, 4),
            "signature_tampering_score": round(self.signature_tampering_score, 4) if self.signature_tampering_score is not None else None,
            "risk_level": self.risk_level,
            "indicator": self.indicator,
            "recommendation": self.recommendation,
            "analysis_status": self.analysis_status,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "analysis_timestamp": self.analysis_timestamp,
            "reference_matches": self.reference_matches,
            "evidence": self.evidence,
        }
