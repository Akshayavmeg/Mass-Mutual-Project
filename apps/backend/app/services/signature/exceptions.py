"""Signature Analysis exceptions (docs/18_Signature_Analysis.md S33)."""

from __future__ import annotations


class ChequeNotExtractedForSignatureError(Exception):
    """Raised when signature analysis is requested before Milestone 3
    extraction (which detects the signature region) has run."""
