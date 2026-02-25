"""RegisterUserCommand dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    """Command to register a new user."""

    name: str
    email: str
    password: str
