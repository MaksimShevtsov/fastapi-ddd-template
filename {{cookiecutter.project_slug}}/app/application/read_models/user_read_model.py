"""UserReadModel for read-side queries."""

from __future__ import annotations

from pydantic import BaseModel


class UserReadModel(BaseModel):
    """Read-optimized user model mapped directly from SQL results."""

    id: str
    name: str
    email: str
    created_at: str
