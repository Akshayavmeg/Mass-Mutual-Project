"""Single, reusable audit-recording abstraction (Milestone 8; docs/27_Audit_Trail.md,
this milestone's explicit instruction #10: "Do NOT make each module
create unrelated custom audit formats. Create one reusable audit
service/repository abstraction.").

Every module that wants to record an audit event calls `record(...)`
here -- never the repository directly -- so the schema stays consistent
project-wide. No secrets are ever accepted into `metadata` (docs/27:
"Do not store secrets in audit metadata"); callers are responsible for
not passing any, and this module never accepts raw request bodies
wholesale for exactly that reason.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.repositories.audit_repository import get_audit_repository


def record(
    *,
    event_type: str,
    cheque_id: str | None = None,
    user_id: str | None = None,
    user_role: str | None = None,
    source: str = "SYSTEM",
    previous_status: str | None = None,
    new_status: str | None = None,
    action: str | None = None,
    result: str | None = None,
    reason: str | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """docs/27 S13 canonical audit_logs field list. `source` is one of
    SYSTEM/USER/API (docs/27 S "source")."""
    event = {
        "event_type": event_type,
        "cheque_id": cheque_id,
        "user_id": user_id,
        "user_role": user_role,
        "source": source,
        "previous_status": previous_status,
        "new_status": new_status,
        "action": action,
        "result": result,
        "reason": reason,
        "request_id": request_id,
        "ip_address": ip_address,
        "metadata": metadata,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return get_audit_repository().record(event)


def get_history(cheque_id: str) -> list[dict]:
    return get_audit_repository().list_for_cheque(cheque_id)
