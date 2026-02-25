"""RefreshTokenRepository implementation using RowQuery."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.interfaces.refresh_token_repository import RefreshTokenRecord, RefreshTokenRepositoryInterface
from app.infrastructure.errors import DatabaseError, DataMappingError


class RefreshTokenRepository(RefreshTokenRepositoryInterface):
    """Concrete refresh token repository using RowQuery transactions."""

    def __init__(self, transaction: Any) -> None:
        self._tx = transaction

    async def save(self, record: RefreshTokenRecord) -> None:
        """Persist a refresh token record."""
        try:
            await self._tx.execute(
                "refresh_tokens.insert",
                {
                    "id": record.id,
                    "user_id": record.user_id,
                    "token_hash": record.token_hash,
                    "expires_at": record.expires_at.isoformat(),
                    "revoked_at": record.revoked_at.isoformat() if record.revoked_at else None,
                    "created_at": record.created_at.isoformat(),
                },
            )
        except Exception as exc:
            raise DatabaseError(message="Failed to save refresh token", cause=exc) from exc

    async def get_by_token_hash(self, token_hash: str) -> RefreshTokenRecord | None:
        """Look up a refresh token by its hash."""
        try:
            row = await self._tx.fetch_one("refresh_tokens.get_by_token_hash", {"token_hash": token_hash})
        except Exception as exc:
            raise DatabaseError(message="Failed to fetch refresh token by hash", cause=exc) from exc
        if row is None:
            return None
        return self._to_record(row)

    async def revoke(self, token_id: str) -> None:
        """Revoke a single refresh token."""
        try:
            await self._tx.execute(
                "refresh_tokens.revoke",
                {"id": token_id, "revoked_at": datetime.now(UTC).isoformat()},
            )
        except Exception as exc:
            raise DatabaseError(message="Failed to revoke refresh token", cause=exc) from exc

    async def revoke_all_for_user(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        try:
            await self._tx.execute(
                "refresh_tokens.revoke_all_for_user",
                {"user_id": user_id, "revoked_at": datetime.now(UTC).isoformat()},
            )
        except Exception as exc:
            raise DatabaseError(message="Failed to revoke all refresh tokens for user", cause=exc) from exc

    @staticmethod
    def _to_record(row: dict) -> RefreshTokenRecord:
        """Map a database row to a RefreshTokenRecord."""
        try:
            raw_expires = row["expires_at"]
            expires_at = (
                raw_expires
                if isinstance(raw_expires, datetime)
                else datetime.fromisoformat(raw_expires)
            )
            raw_revoked = row.get("revoked_at")
            revoked_at = None
            if raw_revoked is not None:
                revoked_at = (
                    raw_revoked
                    if isinstance(raw_revoked, datetime)
                    else datetime.fromisoformat(raw_revoked)
                )
            raw_created = row["created_at"]
            created_at = (
                raw_created
                if isinstance(raw_created, datetime)
                else datetime.fromisoformat(raw_created)
            )
            return RefreshTokenRecord(
                id=row["id"],
                user_id=row["user_id"],
                token_hash=row["token_hash"],
                expires_at=expires_at,
                revoked_at=revoked_at,
                created_at=created_at,
            )
        except (ValueError, KeyError, TypeError) as exc:
            raise DataMappingError(
                message="Failed to map database row to RefreshTokenRecord", cause=exc
            ) from exc
