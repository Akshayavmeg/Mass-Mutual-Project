"""Manual Review Workflow endpoints -- exactly the canonical contract
(docs/26_API_Specification.md S24-S26): GET /reviews,
POST /reviews/{id}/assign, POST /reviews/{id}/complete. Review-case
*creation* has no separate canonical endpoint (see
app/services/review/review_service.py's module docstring) and is not
exposed here.

Reviewer-only operations are enforced server-side via the role/
permission dependency (docs/29 S17, S25) -- not merely hidden in a UI.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse

from app.core.authorization import Permission, require_permission
from app.schemas.review import AssignReviewRequest, CompleteReviewRequest, ReviewCaseResponse, ReviewQueueResponse
from app.services.review import review_service
from app.services.review.exceptions import (
    InvalidReviewDecisionError,
    ReviewCaseAlreadyClosedError,
    ReviewCaseNotFoundError,
    ReviewCommentRequiredError,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": f"REQ-{uuid.uuid4().hex[:12]}"}},
    )


@router.get("", response_model=ReviewQueueResponse)
async def get_review_queue(
    status: str | None = None, priority: str | None = None,
    _role=Depends(require_permission(Permission.REVIEW_VIEW)),
):
    cases = review_service.get_queue(status=status, priority=priority)
    return ReviewQueueResponse(total=len(cases), cases=[ReviewCaseResponse(**c) for c in cases])


@router.post("/{review_case_id}/assign", response_model=ReviewCaseResponse)
async def assign_review_case(
    review_case_id: str, body: AssignReviewRequest,
    _role=Depends(require_permission(Permission.REVIEW_UPDATE)),
):
    try:
        case = review_service.assign_case(review_case_id, reviewer_id=body.reviewer_id)
    except ReviewCaseNotFoundError:
        return _error_response(404, "REVIEW_CASE_NOT_FOUND", "The requested review case does not exist.")
    except ReviewCaseAlreadyClosedError:
        return _error_response(409, "REVIEW_CASE_CLOSED", "This review case is already closed.")
    return ReviewCaseResponse(**case)


@router.post("/{review_case_id}/complete", response_model=ReviewCaseResponse)
async def complete_review_case(
    review_case_id: str, body: CompleteReviewRequest,
    role=Depends(require_permission(Permission.REVIEW_UPDATE)),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
):
    reviewer_id = x_user_id or role.value
    try:
        case = review_service.complete_review(
            review_case_id, decision=body.decision, comment=body.comment, reviewer_id=reviewer_id,
        )
    except ReviewCaseNotFoundError:
        return _error_response(404, "REVIEW_CASE_NOT_FOUND", "The requested review case does not exist.")
    except ReviewCaseAlreadyClosedError:
        return _error_response(409, "REVIEW_CASE_CLOSED", "This review case is already closed.")
    except InvalidReviewDecisionError as exc:
        return _error_response(422, "INVALID_REVIEW_DECISION", str(exc))
    except ReviewCommentRequiredError as exc:
        return _error_response(422, "REVIEW_COMMENT_REQUIRED", str(exc))
    return ReviewCaseResponse(**case)
