"""Manual Review Workflow service (docs/23_Manual_Review_Workflow.md
S5-S23).

Review-case creation is an internal side effect of the Decision Engine
returning REVIEW (docs/23 S3-S4) rather than a directly client-callable
action -- docs/26_API_Specification.md's canonical endpoint table has no
standalone "create review case" endpoint (only GET /reviews, POST
/reviews/{id}/assign, POST /reviews/{id}/complete), so this module is
called from app.services.decision.decision_service, not from a public
API route. See the Milestone 7 report for the full reasoning.

`add_comment` and `escalate_case` are fully implemented, real, tested
service capabilities (satisfying this milestone's reviewer-action
requirements) but are deliberately not given their own dedicated public
endpoints, for the same reason -- ADR-0007 makes docs/26 the canonical
API surface, and it does not list one.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.repositories.review_repository import get_review_repository
from app.services.review import id_generator
from app.services.review.exceptions import (
    InvalidReviewDecisionError,
    ReviewCaseAlreadyClosedError,
    ReviewCaseNotFoundError,
    ReviewCommentRequiredError,
)
from app.services.review.models import REVIEWER_DECISIONS, TERMINAL_STATUSES

_PRIORITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_review_case(cheque_id: str, *, decision_result: dict, record: dict) -> dict:
    """Called by decision_service when decision == REVIEW. Snapshots all
    evidence a reviewer needs (docs/22 S23, docs/23 S7) so the reviewer
    never has to re-fetch or re-derive it from elsewhere."""
    repo = get_review_repository()

    existing = repo.get_by_cheque_id(cheque_id)
    if existing is not None and existing["status"] not in TERMINAL_STATUSES:
        return existing  # do not create a duplicate open case for the same cheque

    review_case_id = id_generator.generate_review_case_id()
    risk_level = decision_result.get("risk_level", "MEDIUM")
    priority = settings.review_priority_by_risk_level.get(risk_level, "MEDIUM")

    extraction = record.get("extraction") or {}
    fields = extraction.get("fields", {})

    case = {
        "review_case_id": review_case_id,
        "cheque_id": cheque_id,
        "status": "QUEUED",
        "priority": priority,
        "trigger_reason": "; ".join(decision_result.get("reasons", [])) or "MANUAL_REVIEW",
        "triggered_rules": decision_result.get("triggered_rules", []),
        "risk_score": decision_result.get("risk_score"),
        "risk_level": risk_level,
        "cheque_summary": {
            "cheque_number": fields.get("cheque_number", {}).get("value"),
            "account_number_masked": _mask_account(fields.get("account_number", {}).get("value")),
            "routing_transit_number": fields.get("routing_transit_number", {}).get("value"),
            "payee_name": fields.get("payee_name", {}).get("value"),
            "amount": fields.get("amount", {}).get("value"),
            "date": fields.get("date", {}).get("value"),
        },
        "validation_results": record.get("validation"),
        "fraud_results": record.get("fraud_analysis"),
        "signature_result": record.get("signature_analysis"),
        "anomaly_results": record.get("anomaly_analysis"),
        "risk_assessment": record.get("risk_assessment"),
        "automated_decision": decision_result,
        "assigned_reviewer_id": None,
        "comments": [],
        "reviewer_decision": None,
        "reviewer_comment": None,
        "final_decision_timestamp": None,
        "escalation_reason": None,
        "created_at": _now(),
        "updated_at": _now(),
        "assigned_at": None,
        "reviewed_at": None,
        "closed_at": None,
        "workflow_version": settings.review_workflow_version,
    }
    repo.save(review_case_id, case)
    return case


def _mask_account(account_number: str | None) -> str | None:
    if not account_number:
        return None
    return f"{'*' * max(0, len(account_number) - 4)}{account_number[-4:]}"


def _get_or_raise(review_case_id: str) -> dict:
    case = get_review_repository().get(review_case_id)
    if case is None:
        raise ReviewCaseNotFoundError(review_case_id)
    return case


def get_case(review_case_id: str) -> dict | None:
    return get_review_repository().get(review_case_id)


def get_queue(*, status: str | None = None, priority: str | None = None) -> list[dict]:
    cases = get_review_repository().list_all()
    if status:
        cases = [c for c in cases if c["status"] == status]
    if priority:
        cases = [c for c in cases if c["priority"] == priority]
    cases.sort(key=lambda c: (_PRIORITY_ORDER.get(c["priority"], 9), c["created_at"]))
    return cases


def assign_case(review_case_id: str, *, reviewer_id: str) -> dict:
    case = _get_or_raise(review_case_id)
    if case["status"] in TERMINAL_STATUSES:
        raise ReviewCaseAlreadyClosedError(review_case_id)
    repo = get_review_repository()
    repo.update(review_case_id, {
        "assigned_reviewer_id": reviewer_id, "status": "ASSIGNED",
        "assigned_at": _now(), "updated_at": _now(),
    })
    return repo.get(review_case_id)


def add_comment(review_case_id: str, *, author: str, comment: str) -> dict:
    case = _get_or_raise(review_case_id)
    if case["status"] in TERMINAL_STATUSES:
        raise ReviewCaseAlreadyClosedError(review_case_id)
    repo = get_review_repository()
    comments = list(case["comments"])
    comments.append({"author": author, "comment": comment, "timestamp": _now()})
    new_status = "UNDER_REVIEW" if case["status"] in ("QUEUED", "ASSIGNED") else case["status"]
    repo.update(review_case_id, {"comments": comments, "status": new_status, "updated_at": _now()})
    return repo.get(review_case_id)


def escalate_case(review_case_id: str, *, reason: str, escalated_by: str) -> dict:
    case = _get_or_raise(review_case_id)
    if case["status"] in TERMINAL_STATUSES:
        raise ReviewCaseAlreadyClosedError(review_case_id)
    repo = get_review_repository()
    repo.update(review_case_id, {
        "status": "ESCALATED", "priority": "CRITICAL", "escalation_reason": reason, "updated_at": _now(),
    })
    return add_comment(review_case_id, author=escalated_by, comment=f"Escalated: {reason}")


def complete_review(review_case_id: str, *, decision: str, comment: str, reviewer_id: str) -> dict:
    """docs/23 S13, S15, S16-S17: the reviewer's decision (APPROVE/REJECT)
    is stored ALONGSIDE the original automated decision, never replacing
    it; a comment is mandatory."""
    case = _get_or_raise(review_case_id)
    if case["status"] in TERMINAL_STATUSES:
        raise ReviewCaseAlreadyClosedError(review_case_id)
    if decision not in REVIEWER_DECISIONS:
        raise InvalidReviewDecisionError(f"decision must be one of {REVIEWER_DECISIONS}, got {decision!r}")
    if not comment or not comment.strip():
        raise ReviewCommentRequiredError("A review reason/comment is required to complete a case.")

    repo = get_review_repository()
    now = _now()
    comments = list(case["comments"])
    comments.append({"author": reviewer_id, "comment": comment, "timestamp": now})
    repo.update(review_case_id, {
        "status": "CLOSED",
        "reviewer_decision": decision,
        "reviewer_comment": comment,
        "assigned_reviewer_id": case.get("assigned_reviewer_id") or reviewer_id,
        "comments": comments,
        "reviewed_at": now,
        "final_decision_timestamp": now,
        "closed_at": now,
        "updated_at": now,
    })

    from app.repositories.cheque_repository import get_cheque_repository
    get_cheque_repository().update(case["cheque_id"], {
        "processing_status": "APPROVED" if decision == "APPROVE" else "REJECTED",
        "human_decision": {
            "decision": decision, "reviewer_id": reviewer_id, "comment": comment, "timestamp": now,
            "review_case_id": review_case_id,
        },
    })
    return repo.get(review_case_id)
