"""DUPLICATE_CHECK -- validation-stage duplicate check
(docs/16_Validation_Engine.md S23).

This is deliberately the *simple*, composite-key exact match described
in docs/16 (Account Number + Cheque Number + Amount + Date) using the
Milestone 1 synthetic processed-cheque history and any other cheques
already processed in this running session. Full multi-level duplicate
detection (image hashing, perceptual/near-duplicate matching, partial-
match heuristics) is docs/19_Duplicate_Detection.md's job and belongs to
Milestone 5 -- not reimplemented here.
"""

from __future__ import annotations

from app.core.config import settings
from app.repositories.banking_repository import BankingDataRepository, BankingDataUnavailableError
from app.services.validation.models import CheckResult


def check_duplicate(
    *,
    cheque_id: str,
    account_number: str | None,
    cheque_number: str | None,
    amount: float | None,
    date_value: str | None,
    banking_repo: BankingDataRepository,
    live_candidates: list[dict],
) -> CheckResult:
    """`live_candidates` is a list of {cheque_id, account_number,
    cheque_number, amount, cheque_date} dicts for other cheques already
    processed in the current session (excluding this one) -- passed in by
    the orchestrator so this validator has no dependency on the cheque
    repository module."""
    severity = settings.validation_severities.get("DUPLICATE_CHECK", "HIGH")

    if not all([account_number, cheque_number, amount is not None, date_value]):
        return CheckResult(
            "DUPLICATE_CHECK", "NOT_CHECKED", severity,
            "Duplicate check requires account number, cheque number, amount, and date.",
        )

    try:
        historical_match = banking_repo.find_duplicate(account_number, cheque_number, amount, date_value)
    except BankingDataUnavailableError as exc:
        return CheckResult(
            "DUPLICATE_CHECK", "NOT_CHECKED", severity, f"Banking data unavailable: {exc}",
        )

    if historical_match is not None:
        return CheckResult(
            "DUPLICATE_CHECK", "FAIL", severity,
            f"Matches previously processed cheque {historical_match.cheque_id}.",
            details={"matched_cheque_id": historical_match.cheque_id},
        )

    for candidate in live_candidates:
        if candidate["cheque_id"] == cheque_id:
            continue
        if (
            candidate.get("account_number") == account_number
            and candidate.get("cheque_number") == cheque_number
            and candidate.get("amount") is not None
            and abs(candidate["amount"] - amount) < 0.01
            and candidate.get("cheque_date") == date_value
        ):
            return CheckResult(
                "DUPLICATE_CHECK", "FAIL", severity,
                f"Matches another cheque processed in this session: {candidate['cheque_id']}.",
                details={"matched_cheque_id": candidate["cheque_id"]},
            )

    return CheckResult("DUPLICATE_CHECK", "PASS", "INFO", "No matching prior record found.")
