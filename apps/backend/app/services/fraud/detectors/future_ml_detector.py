"""ML-ready extension point (docs/17_Fraud_Detection.md S26-S27; ADR-0004).

No supervised model is trained or invoked in Milestone 5 -- ADR-0004
explicitly defers this until a labeled dataset and evaluation
methodology exist. This module documents the interface a future ML
detector would implement so `fraud_service.py` could add it as one more
indicator source (alongside RuleBasedDetector, ImageTamperingDetector,
DuplicateDetector, PatternDetector) without redesigning the engine or
the Decision Engine's contract.

A future implementation would return `FraudIndicator`-shaped evidence
(never a bare "Fraud = TRUE") and would record its own model_name/
model_version, matching docs/17 S26-S27 and ADR-0008 (model versioning).
"""

from __future__ import annotations

from typing import Protocol

from app.services.fraud.models import FraudIndicator


class MLFraudDetector(Protocol):
    """Interface a future ML-based detector must satisfy. Potential
    feature vector per docs/17 S27: amount, cheque_age, account_age,
    cheque_frequency, average_historical_amount, amount_deviation,
    payee_match, account_status, cheque_series_match,
    duplicate_indicator, signature_similarity, image_tampering_score,
    ocr_confidence, validation_failure_count."""

    model_name: str
    model_version: str

    def predict(self, features: dict) -> list[FraudIndicator]: ...
