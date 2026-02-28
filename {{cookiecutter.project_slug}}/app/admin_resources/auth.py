"""Example admin auth provider for demonstration."""

from __future__ import annotations

from app.admin.auth import AdminAuthProvider, AdminUser


class FakeAdminAuthProvider(AdminAuthProvider):
    """Fake auth provider for development/demo. Replace with real auth."""

    def __init__(self) -> None:
        self._users: dict[str, AdminUser] = {
            "1": {"id": "1", "username": "admin", "is_admin": True},
        }
        self._credentials = {"admin": "admin"}

    async def authenticate(self, username: str, password: str) -> AdminUser | None:
        if self._credentials.get(username) == password:
            return self._users["1"]
        return None

    async def get_user(self, user_id: str) -> AdminUser | None:
        return self._users.get(user_id)
