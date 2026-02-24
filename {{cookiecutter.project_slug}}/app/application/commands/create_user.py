"""CreateUserCommand dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUserCommand:
    """Command to create a new user."""

    name: str
    email: str
