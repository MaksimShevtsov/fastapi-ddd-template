"""Example user resource for admin panel demonstration."""

from __future__ import annotations

import uuid
from typing import Any

from app.admin import AdminDAO, ColumnConfig, FieldConfig, FieldType, ResourceAdmin


class InMemoryUserDAO(AdminDAO):
    """In-memory DAO for demonstration. Replace with your real data access."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        # Seed sample data
        for i in range(1, 6):
            uid = str(uuid.uuid4())
            self._store[uid] = {
                "id": uid,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "role": "admin" if i == 1 else "user",
            }

    async def list(
        self, offset: int, limit: int, search: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        items = list(self._store.values())
        if search:
            term = search.lower()
            items = [
                item
                for item in items
                if term in item["name"].lower() or term in item["email"].lower()
            ]
        total = len(items)
        if limit > 0:
            items = items[offset : offset + limit]
        return items, total

    async def get(self, id: str) -> dict[str, Any] | None:
        return self._store.get(id)

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        uid = str(uuid.uuid4())
        record = {"id": uid, **data}
        self._store[uid] = record
        return record

    async def update(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        if id not in self._store:
            raise ValueError(f"Record '{id}' not found")
        self._store[id].update(data)
        return self._store[id]

    async def delete(self, id: str) -> None:
        if id not in self._store:
            raise ValueError(f"Record '{id}' not found")
        del self._store[id]


def create_user_resource() -> ResourceAdmin:
    """Create and return the user ResourceAdmin with an in-memory DAO."""
    return ResourceAdmin(
        name="users",
        display_name="Users",
        dao=InMemoryUserDAO(),
        list_columns=[
            ColumnConfig(name="id", label="ID"),
            ColumnConfig(name="name", label="Name", link_to_detail=True),
            ColumnConfig(name="email", label="Email"),
            ColumnConfig(name="role", label="Role"),
        ],
        form_fields=[
            FieldConfig(name="name", label="Name", field_type=FieldType.TEXT),
            FieldConfig(name="email", label="Email", field_type=FieldType.TEXT),
            FieldConfig(
                name="role",
                label="Role",
                field_type=FieldType.SELECT,
                choices=[("admin", "Admin"), ("user", "User")],
            ),
        ],
    )
