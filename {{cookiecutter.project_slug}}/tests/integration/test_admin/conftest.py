"""Test fixtures for admin panel integration tests."""

from __future__ import annotations

import uuid
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.admin.auth import AdminAuthProvider, AdminUser
from app.admin.resource import ColumnConfig, FieldConfig, FieldType, ResourceAdmin
from app.admin.site import AdminSite


class FakeDAO:
    """In-memory DAO for testing."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def seed(self, records: list[dict[str, Any]]) -> None:
        for r in records:
            self._store[str(r["id"])] = r

    async def list(
        self, offset: int, limit: int, search: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        items = list(self._store.values())
        if search:
            term = search.lower()
            items = [
                item
                for item in items
                if any(term in str(v).lower() for v in item.values())
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


class FakeAuthProvider(AdminAuthProvider):
    """Fake auth provider for testing."""

    async def authenticate(self, username: str, password: str) -> AdminUser | None:
        if username == "admin" and password == "admin":
            return {"id": "1", "username": "admin", "is_admin": True}
        if username == "nonadmin" and password == "nonadmin":
            return {"id": "2", "username": "nonadmin", "is_admin": False}
        return None

    async def get_user(self, user_id: str) -> AdminUser | None:
        if user_id == "1":
            return {"id": "1", "username": "admin", "is_admin": True}
        return None


@pytest.fixture()
def fake_dao() -> FakeDAO:
    dao = FakeDAO()
    dao.seed(
        [
            {"id": "1", "name": "Alice", "email": "alice@example.com", "role": "admin"},
            {"id": "2", "name": "Bob", "email": "bob@example.com", "role": "user"},
            {
                "id": "3",
                "name": "Charlie",
                "email": "charlie@example.com",
                "role": "user",
            },
        ]
    )
    return dao


@pytest.fixture()
def test_resource(fake_dao: FakeDAO) -> ResourceAdmin:
    return ResourceAdmin(
        name="users",
        display_name="Users",
        dao=fake_dao,
        list_columns=[
            ColumnConfig(name="id", label="ID"),
            ColumnConfig(name="name", label="Name", link_to_detail=True),
            ColumnConfig(name="email", label="Email"),
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


@pytest.fixture()
def admin_app(test_resource: ResourceAdmin) -> FastAPI:
    app = FastAPI()
    site = AdminSite(
        title="Test Admin",
        auth_provider=FakeAuthProvider(),
        session_secret="test-secret",
    )
    site.register(test_resource)
    site.mount(app)
    return app


@pytest_asyncio.fixture()
async def client(admin_app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture()
async def authed_client(admin_app: FastAPI) -> AsyncClient:
    """Client with an authenticated admin session."""
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.post(
            "/admin/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        yield c
