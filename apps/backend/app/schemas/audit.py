from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    audit_id: str
    cheque_id: str | None
    event_type: str
    event_timestamp: str | None
    user_id: str | None
    user_role: str | None
    source: str
    previous_status: str | None
    new_status: str | None
    action: str | None
    result: str | None
    reason: str | None
    request_id: str | None
    metadata: dict[str, Any] | None = None


class AuditHistoryResponse(BaseModel):
    """docs/26_API_Specification.md S30.1 Get Cheque Audit History,
    extended with the full docs/27_Audit_Trail.md S13 field set per each
    event -- docs/26's own example shows only {event_type, timestamp}."""

    cheque_id: str
    events: list[AuditEventResponse]
