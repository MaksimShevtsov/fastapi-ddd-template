"""Abstract DAO protocol for admin panel data access."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AdminDAO(Protocol):
    """Data access interface for admin panel resources.

    Developers implement this protocol for each domain resource
    they want to manage through the admin panel.
    """

    async def list(
        self, offset: int, limit: int, search: str | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        """Return (items, total_count) for paginated listing."""
        ...

    async def get(self, id: str) -> dict[str, Any] | None:
        """Return a single record as dict, or None if not found."""
        ...

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a record from form data. Return the created record."""
        ...

    async def update(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a record. Return the updated record."""
        ...

    async def delete(self, id: str) -> None:
        """Delete a record. Raise if not found."""
        ...
