"""Abstract UnitOfWork protocol for the application layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.domain.interfaces.user_repository import UserRepositoryInterface


@runtime_checkable
class UnitOfWork(Protocol):
    """Protocol defining the unit of work contract."""

    @property
    def user_repository(self) -> UserRepositoryInterface: ...

    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None: ...
