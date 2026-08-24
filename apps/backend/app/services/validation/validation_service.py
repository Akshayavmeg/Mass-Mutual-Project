"""Validation Engine orchestrator (docs/16_Validation_Engine.md S7,
S25-S28).

Coordinates all the individual validators against a cheque's Milestone 3
extraction result and the Milestone 1 mock banking data, and assembles
the structured, explainable ValidationSummary.

Module boundary: this service does not declare a cheque fraudulent, does
not calculate a fraud/risk score, and does not approve/reject anything
(docs/16 S47) -- it only produces the evidence those later modules
(Milestones 5 and 7) will consume.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.repositories.banking_repository import BankingDataRepository, get_banking_repository
from app.repositories.cheque_repository import get_cheque_repository
from app.services.validation.exceptions import ChequeNotExtractedError
from app.services.validation.models import CheckResult, ValidationSummary, compute_overall_status
from app.services.validation.validators.account_validator import check_account_exists, check_account_status
from app.services.validation.validators.amount_validator import check_amount, check_amount_consistency
from app.services.validation.validators.cheque_validator import check_cheque_series, check_cheque_status
from app.services.validation.validators.cross_field_validator import check_cross_field
from app.services.validation.validators.date_validator import check_date_window
from app.services.validation.validators.duplicate_validator import check_duplicate
from app.services.validation.validators.payee_validator import check_payee_match
from app.services.validation.validators.required_fields import check_required_fields
from app.services.validation.validators.routing_validator import check_routing_transit


def _field_value(fields: dict, name: str):
    return fields.get(name, {}).get("value")


def _collect_live_duplicate_candidates(cheque_id: str) -> list[dict]:
    repo = get_cheque_repository()
    candidates: list[dict] = []
    for record in repo.list_all():
        if record["cheque_id"] == cheque_id:
            continue
        extraction = record.get("extraction")
        if not extraction:
            continue
        fields = extraction.get("fields", {})
        candidates.append({
            "cheque_id": record["cheque_id"],
            "account_number": _field_value(fields, "account_number"),
            "cheque_number": _field_value(fields, "cheque_number"),
            "amount": _field_value(fields, "amount"),
            "cheque_date": _field_value(fields, "date"),
        })
    return candidates


def validate_cheque(
    cheque_id: str,
    *,
    processing_date: date | None = None,
    banking_repo: BankingDataRepository | None = None,
) -> ValidationSummary:
    repo = get_cheque_repository()
    record = repo.get(cheque_id)
    if record is None:
        raise KeyError(cheque_id)

    extraction = record.get("extraction")
    if extraction is None:
        raise ChequeNotExtractedError(
            "Cheque has not completed OCR/extraction yet; validation cannot run."
        )

    banking_repo = banking_repo or get_banking_repository()
    processing_date = processing_date or datetime.now(timezone.utc).date()
    fields = extraction.get("fields", {})

    checks: dict[str, CheckResult] = {}

    checks["REQUIRED_FIELDS"] = check_required_fields(fields)

    account_number = _field_value(fields, "account_number")
    account_exists_result, account = check_account_exists(account_number, banking_repo)
    checks["ACCOUNT_EXISTS"] = account_exists_result
    checks["ACCOUNT_STATUS"] = check_account_status(account)

    cheque_number = _field_value(fields, "cheque_number")
    checks["CHEQUE_SERIES"] = check_cheque_series(cheque_number, account)
    cheque_status_result, issuance = check_cheque_status(account_number, cheque_number, banking_repo)
    checks["CHEQUE_STATUS"] = cheque_status_result

    date_value = _field_value(fields, "date")
    checks["DATE_WINDOW"] = check_date_window(date_value, processing_date)

    payee_value = _field_value(fields, "payee_name")
    checks["PAYEE_MATCH"] = check_payee_match(payee_value, issuance)

    routing_value = _field_value(fields, "routing_transit_number")
    checks["ROUTING_TRANSIT"] = check_routing_transit(routing_value, account)

    amount_value = _field_value(fields, "amount")
    checks["AMOUNT"] = check_amount(amount_value)

    amount_in_words_value = _field_value(fields, "amount_in_words")
    checks["AMOUNT_CONSISTENCY"] = check_amount_consistency(amount_value, amount_in_words_value)

    live_candidates = _collect_live_duplicate_candidates(cheque_id)
    checks["DUPLICATE_CHECK"] = check_duplicate(
        cheque_id=cheque_id, account_number=account_number, cheque_number=cheque_number,
        amount=amount_value, date_value=date_value, banking_repo=banking_repo,
        live_candidates=live_candidates,
    )

    checks["CROSS_FIELD"] = check_cross_field(checks)

    overall_status = compute_overall_status(checks)
    summary = ValidationSummary(
        cheque_id=cheque_id,
        overall_validation_status=overall_status,
        checks=checks,
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
    )

    repo.update(cheque_id, {
        "validation": summary.as_dict(),
        "processing_status": "VALIDATED",
    })

    return summary


def get_validation_result(cheque_id: str) -> dict | None:
    record = get_cheque_repository().get(cheque_id)
    if record is None:
        return None
    return record.get("validation")
