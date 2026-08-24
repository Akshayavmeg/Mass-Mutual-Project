from __future__ import annotations


class FraudAnalysisNotAvailableError(Exception):
    """Raised when risk scoring is requested before Milestone 5 fraud
    analysis has run -- tampering and duplicate evidence are required
    inputs to the overall risk score (docs/21_Risk_Scoring.md S6-S7)."""
