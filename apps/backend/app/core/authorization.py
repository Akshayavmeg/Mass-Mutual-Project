"""Role-based authorization abstraction (docs/29_User_Roles_and_Access.md
S3, S10, S25-S26).

Per this milestone's own instructions ("use the documented authorization
abstraction and leave full authentication integration to the appropriate
milestone if required"), this implements real, server-side-enforced RBAC
permission checks -- but not a full login/session/JWT flow (no
Authentication milestone has been implemented yet; ADR-0007 documents
JWT bearer auth as the target mechanism for protected endpoints once
built). The caller's role is read from a request header
(`X-User-Role`), which is deliberately NOT trusted as a security
boundary on its own in a real deployment -- it stands in for "the
already-authenticated caller's role" the way a verified JWT claim would,
so the permission-matrix enforcement logic itself is real, tested, and
ready to be wired to real token verification in a later milestone
without changing any endpoint code.
"""

from __future__ import annotations

from enum import Enum

from fastapi import Header, HTTPException


class Role(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    OPERATOR = "OPERATOR"
    REVIEWER = "REVIEWER"
    AUDITOR = "AUDITOR"
    SYSTEM_SERVICE = "SYSTEM_SERVICE"


class Permission(str, Enum):
    CHEQUE_UPLOAD = "CHEQUE_UPLOAD"
    CHEQUE_VIEW = "CHEQUE_VIEW"
    CHEQUE_PROCESS = "CHEQUE_PROCESS"
    REVIEW_VIEW = "REVIEW_VIEW"
    REVIEW_UPDATE = "REVIEW_UPDATE"
    DECISION_APPROVE = "DECISION_APPROVE"
    DECISION_REJECT = "DECISION_REJECT"
    AUDIT_VIEW = "AUDIT_VIEW"


# docs/29 S10 permission matrix / S27 example RBAC configuration.
_ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMINISTRATOR: {
        Permission.CHEQUE_VIEW, Permission.AUDIT_VIEW, Permission.REVIEW_VIEW,
    },
    Role.OPERATOR: {
        Permission.CHEQUE_UPLOAD, Permission.CHEQUE_VIEW, Permission.CHEQUE_PROCESS,
    },
    Role.REVIEWER: {
        Permission.CHEQUE_VIEW, Permission.REVIEW_VIEW, Permission.REVIEW_UPDATE,
        Permission.DECISION_APPROVE, Permission.DECISION_REJECT,
    },
    Role.AUDITOR: {
        Permission.CHEQUE_VIEW, Permission.AUDIT_VIEW,
    },
    Role.SYSTEM_SERVICE: {
        Permission.CHEQUE_VIEW, Permission.CHEQUE_PROCESS,
        Permission.DECISION_APPROVE, Permission.DECISION_REJECT,
    },
}


def role_has_permission(role: Role, permission: Permission) -> bool:
    return permission in _ROLE_PERMISSIONS.get(role, set())


def require_role_header(x_user_role: str | None = Header(default=None)) -> Role:
    """FastAPI dependency: resolves the caller's role from the
    `X-User-Role` header. Missing/unrecognized role -> 401 (docs/29 S17:
    "Authenticated? NO -> 401 Unauthorized")."""
    if not x_user_role:
        raise HTTPException(status_code=401, detail="X-User-Role header is required.")
    try:
        return Role(x_user_role)
    except ValueError:
        raise HTTPException(status_code=401, detail=f"Unknown role: {x_user_role}") from None


def require_permission(permission: Permission):
    """Returns a FastAPI dependency enforcing that the caller's role has
    `permission` -- 403 Forbidden otherwise (docs/29 S17-S18)."""

    def _dependency(x_user_role: str | None = Header(default=None, alias="X-User-Role")) -> Role:  # noqa: B008
        resolved = require_role_header(x_user_role)
        if not role_has_permission(resolved, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Role {resolved.value} does not have permission {permission.value}.",
            )
        return resolved

    return _dependency
