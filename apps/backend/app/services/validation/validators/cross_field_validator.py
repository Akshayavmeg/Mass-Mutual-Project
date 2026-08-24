"""CROSS_FIELD check (docs/16_Validation_Engine.md S24).

docs/16 names five relationship pairs to validate: Account <-> Routing,
Cheque Number <-> Account, Cheque Status <-> Account, Amount <-> Amount
in Words, and Cheque Date <-> Processing Date. Four of those five are
already each their own dedicated, independently-testable check in this
module (ROUTING_TRANSIT, CHEQUE_SERIES, AMOUNT_CONSISTENCY, DATE_WINDOW
respectively) -- re-implementing the same comparisons a second time here
under a different name would just be duplicated logic with no additional
signal.

This check therefore implements the one relationship pair docs/16 names
that has no other dedicated check: Cheque Status <-> Account Status,
i.e. whether the cheque-level and account-level problems are compounding
each other (e.g. a STOPPED cheque on an already-CLOSED account is a
stronger combined signal than either fact alone). It runs after the
other checks and consumes their results, rather than re-deriving raw
field comparisons -- see the Milestone 4 report for this design choice.
"""

from __future__ import annotations

from app.core.config import settings
from app.services.validation.models import CheckResult


def check_cross_field(checks: dict[str, CheckResult]) -> CheckResult:
    severity = settings.validation_severities.get("CROSS_FIELD", "MEDIUM")

    account_status = checks.get("ACCOUNT_STATUS")
    cheque_status = checks.get("CHEQUE_STATUS")

    if account_status is None or cheque_status is None:
        return CheckResult(
            "CROSS_FIELD", "NOT_CHECKED", severity,
            "Cross-field check requires both ACCOUNT_STATUS and CHEQUE_STATUS results.",
        )

    if account_status.status == "FAIL" and cheque_status.status == "FAIL":
        return CheckResult(
            "CROSS_FIELD", "WARNING", severity,
            "Cheque status and account status are both invalid at the same time "
            "(compounded inconsistency between cheque status and account status).",
            details={
                "account_status_message": account_status.message,
                "cheque_status_message": cheque_status.message,
            },
        )

    return CheckResult("CROSS_FIELD", "PASS", "INFO", "No cross-field inconsistencies detected.")
