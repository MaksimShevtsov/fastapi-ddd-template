"""UserRepository implementation using RowQuery."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from app.domain.entities.user import UserEntity
from app.domain.interfaces.user_repository import UserRepositoryInterface
from app.domain.value_objects.user_id import UserId


class UserRepository(UserRepositoryInterface):
    """Concrete user repository using RowQuery transactions."""

    def __init__(self, transaction: Any) -> None:
        self._tx = transaction

    async def get_by_id(self, user_id: UserId) -> UserEntity | None:
        """Fetch a user by ID from the database."""
        row = await self._tx.fetch_one("users.get_by_id", {"id": str(user_id.value)})
        if row is None:
            return None
        return self._to_entity(row)

    async def save(self, user: UserEntity) -> None:
        """Persist a user entity to the database."""
        await self._tx.execute(
            "users.insert",
            {
                "id": str(user.id.value),
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
            },
        )

    async def list_all(self) -> list[UserEntity]:
        """Fetch all users from the database."""
        rows = await self._tx.fetch_all("users.list_all")
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: dict) -> UserEntity:
        """Map a database row to a UserEntity."""
        raw_id = row["id"]
        user_id = UserId(value=raw_id if isinstance(raw_id, uuid.UUID) else uuid.UUID(raw_id))
        raw_created = row["created_at"]
        created_at = raw_created if isinstance(raw_created, datetime) else datetime.fromisoformat(raw_created)
        raw_updated = row.get("updated_at")
        updated_at = raw_updated if raw_updated is None or isinstance(raw_updated, datetime) else datetime.fromisoformat(raw_updated)
        return UserEntity(
            id=user_id,
            name=row["name"],
            email=row["email"],
            created_at=created_at,
            updated_at=updated_at,
        )
