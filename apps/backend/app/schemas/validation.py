from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ValidationCheckResponse(BaseModel):
    check: str
    status: str
    severity: str
    message: str
    details: dict[str, Any] | None = None


class ValidationResultResponse(BaseModel):
    """docs/26_API_Specification.md S13-S14, extended with the per-check
    severity/message/details structure this milestone's "structured,
    explainable validation results" requirement calls for (docs/16
    S25-S28) -- docs/26's own example `checks` object is a flat
    boolean-only illustration; the richer structure here supersedes it,
    consistent with how Milestone 3 extended the OCR result endpoint."""

    cheque_id: str
    overall_validation_status: str
    validation_message: str
    checks: dict[str, ValidationCheckResponse]
    failed_checks: list[str]
    warnings: list[str]
    not_checked: list[str]
    validation_timestamp: str
