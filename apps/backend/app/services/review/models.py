"""Manual review case status vocabulary.

docs/23_Manual_Review_Workflow.md S18 documents this literal 7-state
lifecycle: QUEUED, ASSIGNED, UNDER_REVIEW, ON_HOLD, APPROVED, REJECTED,
CLOSED. This milestone's own instructions separately require "at
minimum" OPEN/IN_REVIEW/RESOLVED/ESCALATED to be supported. Rather than
picking one list over the other, both are honored: docs/23's detailed
statuses are used as the actual `status` field (since "review statuses
should follow the documentation" is the primary instruction), and
ESCALATED is added as a documented extension (docs/23 has no dedicated
escalated status, but S10/S25 and this milestone's instructions both
require an "escalate" action, and docs/29 S14 explicitly lists ESCALATE
as a reviewer outcome). Each of the instruction's four minimum concepts
maps onto a real, distinct status here:

    OPEN      -> QUEUED
    IN_REVIEW -> ASSIGNED or UNDER_REVIEW
    RESOLVED  -> CLOSED
    ESCALATED -> ESCALATED
"""

from __future__ import annotations

STATUSES = ("QUEUED", "ASSIGNED", "UNDER_REVIEW", "ON_HOLD", "ESCALATED", "APPROVED", "REJECTED", "CLOSED")
TERMINAL_STATUSES = ("CLOSED",)
OPEN_STATUS = "QUEUED"  # "OPEN" per this milestone's minimum-status requirement
REVIEWER_DECISIONS = ("APPROVE", "REJECT")
