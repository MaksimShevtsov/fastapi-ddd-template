"""Abstract repository interface for refresh tokens."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class RefreshTokenRecord(ValueObject):
    """Data structure for a stored refresh token."""

    id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime


class RefreshTokenRepositoryInterface(ABC):
    """Abstract refresh token repository contract."""

    @abstractmethod
    async def save(self, record: RefreshTokenRecord) -> None: ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> RefreshTokenRecord | None: ...

    @abstractmethod
    async def revoke(self, token_id: str) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: str) -> None: ...
