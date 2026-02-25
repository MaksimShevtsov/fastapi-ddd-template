"""Concrete UnitOfWork implementation over RowQuery transactions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.errors import DatabaseError

if TYPE_CHECKING:
    from row_query import AsyncEngine

    from app.domain.interfaces.refresh_token_repository import RefreshTokenRepositoryInterface
    from app.domain.interfaces.user_repository import UserRepositoryInterface

logger = logging.getLogger(__name__)


class SqlUnitOfWork:
    """UnitOfWork wrapping a RowQuery transaction."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._transaction: object | None = None
        self._user_repository: UserRepository | None = None
        self._refresh_token_repository: RefreshTokenRepository | None = None

    @property
    def user_repository(self) -> UserRepositoryInterface:
        if self._user_repository is None:
            raise RuntimeError("UnitOfWork not entered")
        return self._user_repository

    @property
    def refresh_token_repository(self) -> RefreshTokenRepositoryInterface:
        if self._refresh_token_repository is None:
            raise RuntimeError("UnitOfWork not entered")
        return self._refresh_token_repository

    async def __aenter__(self) -> SqlUnitOfWork:
        self._transaction = await self._engine.transaction().__aenter__()
        self._user_repository = UserRepository(self._transaction)
        self._refresh_token_repository = RefreshTokenRepository(self._transaction)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self._transaction is not None:
            try:
                await self._transaction.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as exc:
                # Catch unexpected database-level exceptions (connection errors, constraint violations, etc.)
                # and re-raise as DatabaseError so they're properly handled by the infrastructure error handler.
                logger.exception("Database operation failed", exc_info=exc)
                raise DatabaseError(message="Database operation failed", cause=exc) from exc
