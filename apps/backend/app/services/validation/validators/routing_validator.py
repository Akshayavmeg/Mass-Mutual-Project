"""ROUTING_TRANSIT check (docs/16_Validation_Engine.md S20)."""

from __future__ import annotations

from app.core.config import settings
from app.repositories.banking_repository import AccountRecord
from app.services.validation.models import CheckResult


def check_routing_transit(routing_value: str | None, account: AccountRecord | None) -> CheckResult:
    severity = settings.validation_severities.get("ROUTING_TRANSIT", "MEDIUM")

    if not routing_value:
        return CheckResult(
            "ROUTING_TRANSIT", "NOT_CHECKED", severity,
            "Routing/transit number not available from extracted data.",
        )
    if account is None:
        return CheckResult(
            "ROUTING_TRANSIT", "NOT_CHECKED", severity,
            "Routing/transit number cannot be verified because the account was not found.",
        )

    if routing_value == account.routing_number:
        return CheckResult("ROUTING_TRANSIT", "PASS", "INFO", "Routing/transit number matches the banking record.")

    return CheckResult(
        "ROUTING_TRANSIT", "FAIL", severity,
        f"Extracted routing/transit number '{routing_value}' does not match the banking record "
        f"'{account.routing_number}'.",
        details={"extracted": routing_value, "expected": account.routing_number},
    )
