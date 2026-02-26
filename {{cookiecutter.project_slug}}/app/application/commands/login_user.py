"""LoginUserCommand dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginUserCommand:
    """Command to log in a user."""

    email: str
    password: str
