"""Unit tests for the Milestone 7 Manual Review Workflow service
(docs/23_Manual_Review_Workflow.md), covering case lifecycle, reviewer
actions, mandatory-comment enforcement, and duplicate-action prevention.
"""

from __future__ import annotations

import pytest

from app.repositories.cheque_repository import get_cheque_repository
from app.repositories.review_repository import get_review_repository
from app.services.review import review_service
from app.services.review.exceptions import (
    InvalidReviewDecisionError,
    ReviewCaseAlreadyClosedError,
    ReviewCaseNotFoundError,
    ReviewCommentRequiredError,
)


@pytest.fixture(autouse=True)
def _clean_repos():
    yield
    get_review_repository().clear_for_testing()
    get_cheque_repository().clear_for_testing()


def _decision_result(risk_level="MEDIUM"):
    return {"risk_level": risk_level, "risk_score": 40.0, "reasons": ["Test trigger reason."], "triggered_rules": ["TEST_RULE"]}


def _cheque_record(cheque_id="CHK-TEST"):
    get_cheque_repository().save(cheque_id, {
        "cheque_id": cheque_id,
        "extraction": {"fields": {
            "cheque_number": {"value": "000100"}, "account_number": {"value": "9000010001"},
            "payee_name": {"value": "Test Payee"}, "amount": {"value": 100.0}, "date": {"value": "2026-08-01"},
        }},
        "validation": {"overall_validation_status": "PASS"},
        "fraud_analysis": {"risk_level": "LOW"},
    })
    return get_cheque_repository().get(cheque_id)


def test_create_review_case_snapshots_evidence():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    assert case["cheque_id"] == "CHK-TEST"
    assert case["status"] == "QUEUED"
    assert case["priority"] == "MEDIUM"
    assert case["validation_results"] == record["validation"]
    assert case["fraud_results"] == record["fraud_analysis"]
    assert case["cheque_summary"]["cheque_number"] == "000100"


def test_create_review_case_masks_account_number():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    assert case["cheque_summary"]["account_number_masked"] == "******0001"


def test_create_review_case_priority_matches_risk_level():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(risk_level="CRITICAL"), record=record)
    assert case["priority"] == "CRITICAL"


def test_create_review_case_does_not_duplicate_open_case_for_same_cheque():
    record = _cheque_record()
    case1 = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    case2 = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    assert case1["review_case_id"] == case2["review_case_id"]
    assert len(review_service.get_queue()) == 1


def test_get_queue_sorted_by_priority():
    r1 = _cheque_record("CHK-LOW"); r2 = _cheque_record("CHK-CRITICAL")
    review_service.create_review_case("CHK-LOW", decision_result=_decision_result("LOW"), record=r1)
    review_service.create_review_case("CHK-CRITICAL", decision_result=_decision_result("CRITICAL"), record=r2)
    queue = review_service.get_queue()
    assert queue[0]["cheque_id"] == "CHK-CRITICAL"


def test_get_queue_filters_by_status_and_priority():
    record = _cheque_record()
    review_service.create_review_case("CHK-TEST", decision_result=_decision_result("HIGH"), record=record)
    assert len(review_service.get_queue(status="QUEUED")) == 1
    assert len(review_service.get_queue(status="ASSIGNED")) == 0
    assert len(review_service.get_queue(priority="HIGH")) == 1
    assert len(review_service.get_queue(priority="LOW")) == 0


def test_assign_case_updates_status_and_reviewer():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    updated = review_service.assign_case(case["review_case_id"], reviewer_id="USR-002")
    assert updated["status"] == "ASSIGNED"
    assert updated["assigned_reviewer_id"] == "USR-002"
    assert updated["assigned_at"] is not None


def test_assign_unknown_case_raises():
    with pytest.raises(ReviewCaseNotFoundError):
        review_service.assign_case("REV-DOES-NOT-EXIST", reviewer_id="USR-002")


def test_add_comment_transitions_queued_to_under_review():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    updated = review_service.add_comment(case["review_case_id"], author="USR-002", comment="Investigating.")
    assert updated["status"] == "UNDER_REVIEW"
    assert len(updated["comments"]) == 1
    assert updated["comments"][0]["comment"] == "Investigating."


def test_escalate_case_sets_status_and_critical_priority():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result("LOW"), record=record)
    updated = review_service.escalate_case(case["review_case_id"], reason="Needs supervisor input.", escalated_by="USR-002")
    assert updated["status"] == "ESCALATED"
    assert updated["priority"] == "CRITICAL"
    assert updated["escalation_reason"] == "Needs supervisor input."
    assert any("Escalated" in c["comment"] for c in updated["comments"])


def test_complete_review_approve_closes_case_and_updates_cheque():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    updated = review_service.complete_review(case["review_case_id"], decision="APPROVE", comment="Verified manually.", reviewer_id="USR-002")
    assert updated["status"] == "CLOSED"
    assert updated["reviewer_decision"] == "APPROVE"
    assert updated["reviewer_comment"] == "Verified manually."
    assert updated["closed_at"] is not None

    cheque = get_cheque_repository().get("CHK-TEST")
    assert cheque["processing_status"] == "APPROVED"
    assert cheque["human_decision"]["decision"] == "APPROVE"


def test_complete_review_preserves_automated_decision_alongside_human_decision():
    """docs/23 S16-S17: the automated decision must never be overwritten
    -- both must remain available."""
    record = _cheque_record()
    automated = _decision_result()
    case = review_service.create_review_case("CHK-TEST", decision_result=automated, record=record)
    updated = review_service.complete_review(case["review_case_id"], decision="REJECT", comment="Not verified.", reviewer_id="USR-002")
    assert updated["automated_decision"]["reasons"] == automated["reasons"]
    assert updated["reviewer_decision"] == "REJECT"


def test_complete_review_requires_nonempty_comment():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    with pytest.raises(ReviewCommentRequiredError):
        review_service.complete_review(case["review_case_id"], decision="APPROVE", comment="", reviewer_id="USR-002")
    with pytest.raises(ReviewCommentRequiredError):
        review_service.complete_review(case["review_case_id"], decision="APPROVE", comment="   ", reviewer_id="USR-002")


def test_complete_review_rejects_invalid_decision_value():
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    with pytest.raises(InvalidReviewDecisionError):
        review_service.complete_review(case["review_case_id"], decision="ESCALATE", comment="x", reviewer_id="USR-002")


def test_duplicate_action_prevention_already_closed_case():
    """docs/23 S31 Test Case 3 / this milestone's explicit
    already-resolved-case requirement."""
    record = _cheque_record()
    case = review_service.create_review_case("CHK-TEST", decision_result=_decision_result(), record=record)
    review_service.complete_review(case["review_case_id"], decision="APPROVE", comment="Done.", reviewer_id="USR-002")

    with pytest.raises(ReviewCaseAlreadyClosedError):
        review_service.complete_review(case["review_case_id"], decision="REJECT", comment="Change my mind.", reviewer_id="USR-003")
    with pytest.raises(ReviewCaseAlreadyClosedError):
        review_service.assign_case(case["review_case_id"], reviewer_id="USR-003")
    with pytest.raises(ReviewCaseAlreadyClosedError):
        review_service.add_comment(case["review_case_id"], author="USR-003", comment="late comment")
    with pytest.raises(ReviewCaseAlreadyClosedError):
        review_service.escalate_case(case["review_case_id"], reason="too late", escalated_by="USR-003")
