"""User read-model queries using RowQuery."""

from __future__ import annotations

from typing import Any

from app.application.read_models.user_read_model import UserReadModel


async def fetch_user_by_id(engine: Any, user_id: str) -> UserReadModel | None:
    """Fetch a single user by ID using RowQuery SQL registry."""
    row = await engine.fetch_one("users.get_by_id", {"id": user_id})
    if row is None:
        return None
    return UserReadModel(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        created_at=str(row["created_at"]),
    )


async def fetch_all_users(engine: Any) -> list[UserReadModel]:
    """Fetch all users using RowQuery SQL registry."""
    rows = await engine.fetch_all("users.list_all")
    return [
        UserReadModel(
            id=str(row["id"]),
            name=row["name"],
            email=row["email"],
            created_at=str(row["created_at"]),
        )
        for row in rows
    ]
