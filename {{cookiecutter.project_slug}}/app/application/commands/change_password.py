"""ChangePasswordCommand dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChangePasswordCommand:
    """Command to change a user's password."""

    user_id: str
    old_password: str
    new_password: str
