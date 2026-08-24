"""Unit tests for the reusable AuditService abstraction (Milestone 8;
docs/27_Audit_Trail.md), against the in-memory fallback repository
(fully testable without a live database -- the PostgreSQL-backed
repository's own SQL is exercised separately via the ORM/migration
tests, since no live server is available in this environment).
"""

from __future__ import annotations

import pytest

from app.repositories.audit_repository import get_audit_repository
from app.services.audit import audit_service


@pytest.fixture(autouse=True)
def _clean_audit_log():
    yield
    repo = get_audit_repository()
    if hasattr(repo, "clear_for_testing"):
        repo.clear_for_testing()


def test_record_stores_all_canonical_fields():
    event = audit_service.record(
        event_type="CHEQUE_UPLOADED", cheque_id="CHK-1", user_id="USR-1", user_role="OPERATOR",
        source="USER", previous_status=None, new_status="UPLOADED", action="UPLOAD",
        result="SUCCESS", reason="test", request_id="REQ-1", metadata={"key": "value"},
    )
    assert event["event_type"] == "CHEQUE_UPLOADED"
    assert event["cheque_id"] == "CHK-1"
    assert event["source"] == "USER"
    assert event["metadata"] == {"key": "value"}
    assert "audit_id" in event
    assert "event_timestamp" in event


def test_record_defaults_source_to_system():
    event = audit_service.record(event_type="OCR_COMPLETED", cheque_id="CHK-1")
    assert event["source"] == "SYSTEM"


def test_get_history_returns_only_events_for_that_cheque():
    audit_service.record(event_type="CHEQUE_UPLOADED", cheque_id="CHK-A")
    audit_service.record(event_type="CHEQUE_UPLOADED", cheque_id="CHK-B")
    audit_service.record(event_type="OCR_COMPLETED", cheque_id="CHK-A")

    history_a = audit_service.get_history("CHK-A")
    assert len(history_a) == 2
    assert all(e["cheque_id"] == "CHK-A" for e in history_a)


def test_get_history_empty_for_unknown_cheque():
    assert audit_service.get_history("CHK-DOES-NOT-EXIST") == []


def test_audit_log_is_append_only_no_update_or_delete_method_exposed():
    """docs/27: audit records must remain append-only from the
    application's perspective."""
    repo = get_audit_repository()
    assert not hasattr(repo, "update")
    assert not hasattr(repo, "delete")


def test_each_event_gets_a_unique_audit_id():
    e1 = audit_service.record(event_type="CHEQUE_UPLOADED", cheque_id="CHK-1")
    e2 = audit_service.record(event_type="OCR_COMPLETED", cheque_id="CHK-1")
    assert e1["audit_id"] != e2["audit_id"]
