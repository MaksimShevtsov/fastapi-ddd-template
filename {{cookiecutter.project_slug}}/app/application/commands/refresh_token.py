"""RefreshTokenCommand dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshTokenCommand:
    """Command to refresh an access token."""

    refresh_token: str
