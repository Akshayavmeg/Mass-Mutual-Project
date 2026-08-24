from __future__ import annotations

from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    """docs/26_API_Specification.md S31 (GET /users/me).

    No login/JWT milestone exists yet (ADR-0007 documents JWT as the
    target mechanism once an Authentication milestone is built). This
    reflects the caller's already-resolved dev-mode role (X-User-Role /
    X-User-Id headers, see app/core/authorization.py) back as a user
    profile -- a development/MVP stand-in, not a real user directory
    lookup, as Milestone 9's own instructions direct for this case."""

    user_id: str
    username: str
    role: str
    status: str
