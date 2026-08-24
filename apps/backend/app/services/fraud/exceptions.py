"""Fraud Detection Engine exceptions (docs/17_Fraud_Detection.md S37
Reliability: "Failures in fraud analysis should not result in automatic
approval.")"""

from __future__ import annotations


class ChequeNotValidatedError(Exception):
    """Raised when fraud analysis is requested before Milestone 4
    validation has run. The fraud engine consumes validation results
    (docs/17 S5) rather than re-deriving them, so it cannot proceed
    without them."""
