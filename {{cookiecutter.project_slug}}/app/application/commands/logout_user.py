"""LogoutUserCommand dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutUserCommand:
    """Command to log out a user by revoking their refresh token."""

    refresh_token: str
