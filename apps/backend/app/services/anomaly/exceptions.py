from __future__ import annotations


class ChequeNotExtractedForAnomalyError(Exception):
    """Raised when anomaly analysis is requested before Milestone 3
    extraction has run (account/cheque/amount/payee fields are required)."""
