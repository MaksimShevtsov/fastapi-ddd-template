"""RowQuery AsyncEngine factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from row_query import AsyncEngine, ConnectionConfig, SQLRegistry

if TYPE_CHECKING:
    from app.infrastructure.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create and configure the async database engine."""
    config = ConnectionConfig(url=settings.database_url)
    registry = SQLRegistry(directory="app/infrastructure/sql")
    return AsyncEngine(config=config, registry=registry)
