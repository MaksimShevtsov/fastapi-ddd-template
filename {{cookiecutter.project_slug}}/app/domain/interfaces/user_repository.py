"""Abstract repository interface for User entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.user import UserEntity
    from app.domain.value_objects.user_id import UserId


class UserRepositoryInterface(ABC):
    """Abstract User repository contract for the domain layer."""

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> UserEntity | None: ...

    @abstractmethod
    async def save(self, user: UserEntity) -> None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None: ...

    @abstractmethod
    async def list_all(self) -> list[UserEntity]: ...
