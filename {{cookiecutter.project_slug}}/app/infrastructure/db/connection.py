"""RowQuery AsyncEngine factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from row_query import AsyncEngine, ConnectionConfig, SQLRegistry

if TYPE_CHECKING:
    from app.infrastructure.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create and configure the async database engine."""
    if settings.db_driver == "postgresql":
        config = ConnectionConfig(
            driver="postgresql",
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )
    else:
        config = ConnectionConfig(driver="sqlite", database=settings.db_name)
    registry = SQLRegistry(directory="app/infrastructure/sql")
    return AsyncEngine.from_config(config, registry)
