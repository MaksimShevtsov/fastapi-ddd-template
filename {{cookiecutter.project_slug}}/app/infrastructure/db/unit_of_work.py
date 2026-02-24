"""Concrete UnitOfWork implementation over RowQuery transactions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from row_query import AsyncEngine

    from app.domain.interfaces.user_repository import UserRepositoryInterface


class SqlUnitOfWork:
    """UnitOfWork wrapping a RowQuery transaction."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._transaction: object | None = None
        self._user_repository: UserRepository | None = None

    @property
    def user_repository(self) -> UserRepositoryInterface:
        if self._user_repository is None:
            raise RuntimeError("UnitOfWork not entered")
        return self._user_repository

    async def __aenter__(self) -> SqlUnitOfWork:
        self._transaction = await self._engine.transaction().__aenter__()
        self._user_repository = UserRepository(self._transaction)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self._transaction is not None:
            await self._transaction.__aexit__(exc_type, exc_val, exc_tb)
