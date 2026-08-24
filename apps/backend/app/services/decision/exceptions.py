from __future__ import annotations


class RiskAssessmentNotAvailableError(Exception):
    """Raised when a decision is requested before Milestone 6 risk
    scoring has run -- the Decision Engine consumes the risk assessment
    rather than computing anything itself (docs/22 S4)."""
