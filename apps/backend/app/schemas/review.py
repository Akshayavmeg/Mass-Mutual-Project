from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ReviewCaseResponse(BaseModel):
    """docs/26_API_Specification.md S24-S26, extended with the full case
    detail docs/22 S23 / docs/23 S6-S7 require (each queue item already
    carries everything a reviewer needs -- no separate single-case-detail
    endpoint exists in the canonical docs/26 list)."""

    review_case_id: str
    cheque_id: str
    status: str
    priority: str
    trigger_reason: str
    triggered_rules: list[str]
    risk_score: float | None
    risk_level: str
    cheque_summary: dict[str, Any]
    validation_results: dict[str, Any] | None
    fraud_results: dict[str, Any] | None
    signature_result: dict[str, Any] | None
    anomaly_results: dict[str, Any] | None
    risk_assessment: dict[str, Any] | None
    automated_decision: dict[str, Any]
    assigned_reviewer_id: str | None
    comments: list[dict[str, Any]]
    reviewer_decision: str | None
    reviewer_comment: str | None
    final_decision_timestamp: str | None
    escalation_reason: str | None
    created_at: str
    updated_at: str
    assigned_at: str | None
    reviewed_at: str | None
    closed_at: str | None
    workflow_version: str


class ReviewQueueResponse(BaseModel):
    total: int
    cases: list[ReviewCaseResponse]


class AssignReviewRequest(BaseModel):
    reviewer_id: str


class CompleteReviewRequest(BaseModel):
    decision: str
    comment: str
