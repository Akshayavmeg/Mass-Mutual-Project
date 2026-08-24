"""PostgreSQL-backed implementation of ReviewCaseRepository (Milestone
8), matching app.repositories.review_repository.InMemoryReviewCaseRepository's
interface exactly so app.services.review.review_service does not change.
"""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.core.database import SessionLocal
from app.models.review import ManualReviewCase

_CORE_FIELDS = {
    "review_case_id", "cheque_id", "priority", "trigger_reason", "status",
    "assigned_reviewer_id", "reviewer_decision", "reviewer_comment", "comments",
    "automated_decision", "risk_score", "escalation_reason", "created_at",
    "assigned_at", "reviewed_at", "closed_at", "updated_at",
}


def _to_dict(row: ManualReviewCase) -> dict:
    base = {
        "review_case_id": row.review_case_id,
        "cheque_id": row.cheque_id,
        "priority": row.priority,
        "trigger_reason": row.trigger_reason,
        "status": row.status,
        "assigned_reviewer_id": str(row.assigned_reviewer_id) if row.assigned_reviewer_id else None,
        "reviewer_decision": row.reviewer_decision,
        "reviewer_comment": row.reviewer_comment,
        "comments": row.comments or [],
        "automated_decision": row.automated_decision or {},
        "risk_score": float(row.risk_score) if row.risk_score is not None else None,
        "escalation_reason": row.escalation_reason,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "assigned_at": row.assigned_at.isoformat() if row.assigned_at else None,
        "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
        "closed_at": row.closed_at.isoformat() if row.closed_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }
    # `full_case` may carry extra snapshot fields (e.g. cheque_summary,
    # validation_results) not represented as their own typed columns;
    # the typed columns above always take precedence for the fields they
    # do cover, since they are the source of truth after any update().
    return {**(row.full_case or {}), **base}


class PostgresReviewCaseRepository:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    def save(self, review_case_id: str, record: dict) -> None:
        with self._session_factory() as session:
            row = ManualReviewCase(review_case_id=review_case_id, cheque_id=record["cheque_id"], priority=record.get("priority", "MEDIUM"), trigger_reason=record.get("trigger_reason", ""), status=record.get("status", "QUEUED"))
            session.merge(row)
            self._apply(session, review_case_id, record)
            session.commit()

    def get(self, review_case_id: str) -> dict | None:
        with self._session_factory() as session:
            row = session.get(ManualReviewCase, review_case_id)
            return _to_dict(row) if row else None

    def update(self, review_case_id: str, updates: dict) -> None:
        with self._session_factory() as session:
            row = session.get(ManualReviewCase, review_case_id)
            if row is None:
                raise KeyError(review_case_id)
            self._apply(session, review_case_id, updates, row=row)
            session.commit()

    def list_all(self) -> list[dict]:
        with self._session_factory() as session:
            return [_to_dict(r) for r in session.query(ManualReviewCase).all()]

    def get_by_cheque_id(self, cheque_id: str) -> dict | None:
        with self._session_factory() as session:
            row = session.query(ManualReviewCase).filter_by(cheque_id=cheque_id).order_by(ManualReviewCase.created_at.desc()).first()
            return _to_dict(row) if row else None

    def clear_for_testing(self) -> None:
        with self._session_factory() as session:
            session.query(ManualReviewCase).delete()
            session.commit()

    def _apply(self, session: Session, review_case_id: str, data: dict, row: ManualReviewCase | None = None) -> None:
        row = row or session.get(ManualReviewCase, review_case_id)
        snapshot = dict(row.full_case or {})
        for key, value in data.items():
            if key == "status":
                row.status = value
            elif key == "priority":
                row.priority = value
            elif key == "assigned_reviewer_id":
                row.assigned_reviewer_id = None  # reviewer_id is a plain string identifier, not a users.user_id FK yet (no auth/user table wired -- see Milestone 8 report)
            elif key == "reviewer_decision":
                row.reviewer_decision = value
            elif key == "reviewer_comment":
                row.reviewer_comment = value
            elif key == "comments":
                row.comments = value
            elif key == "automated_decision":
                row.automated_decision = value
            elif key == "risk_score":
                row.risk_score = value
            elif key == "escalation_reason":
                row.escalation_reason = value
            elif key in ("assigned_at", "reviewed_at", "closed_at", "updated_at", "created_at"):
                pass  # server-managed / parsed from ISO strings not required for this MVP's read path
            snapshot[key] = value
        row.full_case = snapshot
