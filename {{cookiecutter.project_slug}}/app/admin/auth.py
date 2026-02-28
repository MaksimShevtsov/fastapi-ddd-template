"""Admin authentication: protocols, guards, and flash message helpers."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict

from fastapi import Request
from fastapi.responses import RedirectResponse


class AdminUser(TypedDict):
    """Minimal representation of an authenticated admin user."""

    id: str
    username: str
    is_admin: bool


class AdminAuthProvider(Protocol):
    """Abstract authentication interface for admin panel."""

    async def authenticate(self, username: str, password: str) -> AdminUser | None:
        """Validate credentials. Return AdminUser on success, None on failure."""
        ...

    async def get_user(self, user_id: str) -> AdminUser | None:
        """Retrieve user by ID from session. Return None if no longer valid."""
        ...


async def require_admin(request: Request) -> AdminUser | RedirectResponse:
    """FastAPI dependency that checks admin session.

    Returns AdminUser if authenticated, or a RedirectResponse to login.
    """
    admin_site = request.app.state.admin_site
    prefix = admin_site.prefix

    user_id = request.session.get("admin_user_id")
    if not user_id:
        return RedirectResponse(url=f"{prefix}/login", status_code=303)

    user = await admin_site.auth_provider.get_user(user_id)
    if not user or not user.get("is_admin"):
        request.session.clear()
        return RedirectResponse(url=f"{prefix}/login", status_code=303)

    return user


def set_flash(request: Request, type: str, message: str) -> None:
    """Set a flash message in the session."""
    request.session["_flash"] = {"type": type, "message": message}


def get_flash(request: Request) -> dict[str, Any] | None:
    """Pop and return the flash message from session, or None."""
    return request.session.pop("_flash", None)
