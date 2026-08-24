from __future__ import annotations


class ChequeNotExtractedError(Exception):
    """Raised when validation is requested for a cheque that hasn't
    completed Milestone 3 extraction yet."""
