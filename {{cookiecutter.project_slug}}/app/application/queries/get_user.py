"""GetUserQuery dataclass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserQuery:
    """Query to retrieve a user by ID."""

    user_id: str
