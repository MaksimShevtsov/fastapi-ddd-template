"""Dependency wiring for FastAPI injection."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, AsyncIterator

from fastapi import Depends, Request

from app.application.bus.command_bus import CommandBus
from app.application.bus.query_bus import QueryBus
from app.infrastructure.config import Settings
from app.infrastructure.db.unit_of_work import SqlUnitOfWork

if TYPE_CHECKING:
    from row_query import AsyncEngine

    from app.application.unit_of_work import UnitOfWork


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


def get_engine(request: Request) -> AsyncEngine:
    """Return the async database engine from app state."""
    return request.app.state.engine


@lru_cache
def get_command_bus() -> CommandBus:
    """Return the command bus singleton."""
    return CommandBus()


@lru_cache
def get_query_bus() -> QueryBus:
    """Return the query bus singleton."""
    return QueryBus()


async def get_unit_of_work(
    engine: AsyncEngine = Depends(get_engine),
) -> AsyncIterator[UnitOfWork]:
    """Provide a unit of work for the request scope."""
    uow = SqlUnitOfWork(engine)
    yield uow
