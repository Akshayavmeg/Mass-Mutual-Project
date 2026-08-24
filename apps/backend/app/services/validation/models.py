"""Structured validation result types (docs/16_Validation_Engine.md S25-S28).

The Validation Engine produces explainable evidence, not a fraud/decision
verdict -- see the module boundary notes on ValidationSummary below.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STATUSES = ("PASS", "FAIL", "WARNING", "NOT_CHECKED", "NOT_APPLICABLE")
SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")


@dataclass(frozen=True)
class CheckResult:
    check: str
    status: str  # one of STATUSES
    severity: str  # one of SEVERITIES
    message: str
    details: dict[str, Any] | None = None

    def as_dict(self) -> dict:
        return {
            "check": self.check,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class ValidationSummary:
    """The Validation Engine's complete output for one cheque.

    Module boundary (docs/16 S47): this object is EVIDENCE for the Fraud
    Detection and Decision Engine modules (Milestones 5 and 7) -- it does
    not itself declare the cheque fraudulent, does not calculate a fraud
    score, and does not approve/reject anything. `overall_validation_status`
    describes whether the extracted data is internally/externally
    consistent with the mock banking records, nothing more.
    """

    cheque_id: str
    overall_validation_status: str
    checks: dict[str, CheckResult] = field(default_factory=dict)
    validation_timestamp: str = ""

    @property
    def failed_checks(self) -> list[str]:
        return [name for name, c in self.checks.items() if c.status == "FAIL"]

    @property
    def warnings(self) -> list[str]:
        return [name for name, c in self.checks.items() if c.status == "WARNING"]

    @property
    def not_checked(self) -> list[str]:
        return [name for name, c in self.checks.items() if c.status == "NOT_CHECKED"]

    @property
    def validation_message(self) -> str:
        if self.failed_checks:
            return f"{len(self.failed_checks)} check(s) failed: {', '.join(self.failed_checks)}."
        if self.not_checked:
            return f"{len(self.not_checked)} check(s) could not be verified: {', '.join(self.not_checked)}."
        if self.warnings:
            return f"{len(self.warnings)} check(s) produced a warning: {', '.join(self.warnings)}."
        return "All validation checks passed."

    def as_dict(self) -> dict:
        return {
            "cheque_id": self.cheque_id,
            "overall_validation_status": self.overall_validation_status,
            "validation_message": self.validation_message,
            "checks": {name: c.as_dict() for name, c in self.checks.items()},
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "not_checked": self.not_checked,
            "validation_timestamp": self.validation_timestamp,
        }


def compute_overall_status(checks: dict[str, CheckResult]) -> str:
    """Fail-safe aggregation (docs/16 S3, S42): a FAIL anywhere fails the
    whole validation; a NOT_CHECKED or WARNING anywhere prevents a clean
    PASS (NOT_CHECKED must never be silently treated as equivalent to
    PASS) -- only WARNING/NOT_CHECKED-free, all-PASS-or-NOT_APPLICABLE
    results count as an overall PASS."""
    statuses = {c.status for c in checks.values()}
    if "FAIL" in statuses:
        return "FAIL"
    if "WARNING" in statuses or "NOT_CHECKED" in statuses:
        return "WARNING"
    return "PASS"
