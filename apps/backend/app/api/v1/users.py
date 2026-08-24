"""User API (docs/26_API_Specification.md S31). See
app/schemas/user.py's module docstring: this is a dev-mode reflection of
the caller's resolved role, not a real user directory."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header

from app.core.authorization import Role, require_role_header
from app.schemas.user import CurrentUserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    role: Role = Depends(require_role_header),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
):
    user_id = x_user_id or f"DEV-{role.value}"
    return CurrentUserResponse(
        user_id=user_id,
        username=f"{role.value.lower()}_dev",
        role=role.value,
        status="ACTIVE",
    )
