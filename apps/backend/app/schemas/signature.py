from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SignatureAnalysisResponse(BaseModel):
    """docs/26_API_Specification.md S17, extended with the full
    structured output docs/18_Signature_Analysis.md S23 requires
    (image_quality, analysis_confidence, tampering score, indicator,
    recommendation, model name/version) -- docs/26's own example
    (`similarity_score` on an apparent 0-100 scale, a flat `status`
    enum) is superseded here by docs/18's own authoritative 0.00-1.00
    scale and richer status vocabulary, consistent with how Milestones
    3-5 extended their own flat docs/26 examples."""

    cheque_id: str
    account_number: str | None
    signature_present: bool
    image_quality: str
    similarity_score: float | None
    analysis_confidence: float
    signature_tampering_score: float | None
    risk_level: str
    indicator: str | None
    recommendation: str
    analysis_status: str
    model_name: str
    model_version: str
    analysis_timestamp: str
    reference_matches: list[dict[str, Any]]
    evidence: dict[str, Any] | None = None
