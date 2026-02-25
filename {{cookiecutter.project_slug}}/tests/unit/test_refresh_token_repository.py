"""Tests for RefreshTokenRepository error handling."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.domain.interfaces.refresh_token_repository import RefreshTokenRecord
from app.infrastructure.db.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.infrastructure.errors import DatabaseError, DataMappingError


class TestRefreshTokenRepositorySave:
    """Test RefreshTokenRepository.save()."""

    @pytest.mark.asyncio
    async def test_save_success(self):
        """Successfully save a refresh token."""
        record = RefreshTokenRecord(
            id="token-123",
            user_id="user-456",
            token_hash="hash-xyz",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            revoked_at=None,
            created_at=datetime.now(UTC),
        )

        mock_tx = AsyncMock()
        repo = RefreshTokenRepository(mock_tx)
        await repo.save(record)

        mock_tx.execute.assert_called_once()
        call_args = mock_tx.execute.call_args
        assert call_args[0][0] == "refresh_tokens.insert"
        assert call_args[0][1]["id"] == "token-123"
        assert call_args[0][1]["user_id"] == "user-456"

    @pytest.mark.asyncio
    async def test_save_database_error(self):
        """Raise DatabaseError when save fails."""
        record = RefreshTokenRecord(
            id="token-789",
            user_id="user-999",
            token_hash="hash-abc",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            revoked_at=None,
            created_at=datetime.now(UTC),
        )

        mock_tx = AsyncMock()
        mock_tx.execute.side_effect = Exception("Foreign key constraint failed")

        repo = RefreshTokenRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.save(record)

        assert exc_info.value.message == "Failed to save refresh token"
        assert "Foreign key constraint failed" in str(exc_info.value.cause)


class TestRefreshTokenRepositoryGetByTokenHash:
    """Test RefreshTokenRepository.get_by_token_hash()."""

    @pytest.mark.asyncio
    async def test_get_by_token_hash_success(self):
        """Successfully fetch a refresh token by hash."""
        mock_row = {
            "id": "token-123",
            "user_id": "user-456",
            "token_hash": "hash-xyz",
            "expires_at": datetime.now(UTC) + timedelta(days=7),
            "revoked_at": None,
            "created_at": datetime.now(UTC),
        }

        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = mock_row

        repo = RefreshTokenRepository(mock_tx)
        result = await repo.get_by_token_hash("hash-xyz")

        assert result is not None
        assert result.id == "token-123"
        assert result.user_id == "user-456"
        mock_tx.fetch_one.assert_called_once_with(
            "refresh_tokens.get_by_token_hash", {"token_hash": "hash-xyz"}
        )

    @pytest.mark.asyncio
    async def test_get_by_token_hash_not_found(self):
        """Return None when token not found."""
        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = None

        repo = RefreshTokenRepository(mock_tx)
        result = await repo.get_by_token_hash("nonexistent-hash")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_token_hash_database_error(self):
        """Raise DatabaseError when database operation fails."""
        mock_tx = AsyncMock()
        mock_tx.fetch_one.side_effect = Exception("Connection pool exhausted")

        repo = RefreshTokenRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.get_by_token_hash("some-hash")

        assert exc_info.value.message == "Failed to fetch refresh token by hash"
        assert str(exc_info.value.cause) == "Connection pool exhausted"


class TestRefreshTokenRepositoryRevoke:
    """Test RefreshTokenRepository.revoke()."""

    @pytest.mark.asyncio
    async def test_revoke_success(self):
        """Successfully revoke a refresh token."""
        mock_tx = AsyncMock()
        repo = RefreshTokenRepository(mock_tx)
        await repo.revoke("token-123")

        mock_tx.execute.assert_called_once()
        call_args = mock_tx.execute.call_args
        assert call_args[0][0] == "refresh_tokens.revoke"
        assert call_args[0][1]["id"] == "token-123"

    @pytest.mark.asyncio
    async def test_revoke_database_error(self):
        """Raise DatabaseError when revoke fails."""
        mock_tx = AsyncMock()
        mock_tx.execute.side_effect = Exception("Update failed")

        repo = RefreshTokenRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.revoke("token-456")

        assert exc_info.value.message == "Failed to revoke refresh token"
        assert str(exc_info.value.cause) == "Update failed"


class TestRefreshTokenRepositoryRevokeAllForUser:
    """Test RefreshTokenRepository.revoke_all_for_user()."""

    @pytest.mark.asyncio
    async def test_revoke_all_for_user_success(self):
        """Successfully revoke all tokens for a user."""
        mock_tx = AsyncMock()
        repo = RefreshTokenRepository(mock_tx)
        await repo.revoke_all_for_user("user-789")

        mock_tx.execute.assert_called_once()
        call_args = mock_tx.execute.call_args
        assert call_args[0][0] == "refresh_tokens.revoke_all_for_user"
        assert call_args[0][1]["user_id"] == "user-789"

    @pytest.mark.asyncio
    async def test_revoke_all_for_user_database_error(self):
        """Raise DatabaseError when bulk revoke fails."""
        mock_tx = AsyncMock()
        mock_tx.execute.side_effect = Exception("Batch update timeout")

        repo = RefreshTokenRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.revoke_all_for_user("user-999")

        assert exc_info.value.message == "Failed to revoke all refresh tokens for user"
        assert str(exc_info.value.cause) == "Batch update timeout"


class TestRefreshTokenRepositoryDataMapping:
    """Test RefreshTokenRepository data mapping error handling."""

    @pytest.mark.asyncio
    async def test_to_record_mapping_error_missing_field(self):
        """Raise DataMappingError when required field is missing."""
        mock_row = {
            "id": "token-123",
            "user_id": "user-456",
            # Missing 'token_hash'
            "expires_at": datetime.now(UTC),
            "created_at": datetime.now(UTC),
        }

        with pytest.raises(DataMappingError) as exc_info:
            RefreshTokenRepository._to_record(mock_row)

        assert "Failed to map database row to RefreshTokenRecord" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_to_record_mapping_error_invalid_datetime(self):
        """Raise DataMappingError when datetime is invalid."""
        mock_row = {
            "id": "token-123",
            "user_id": "user-456",
            "token_hash": "hash-xyz",
            "expires_at": "not-a-datetime",
            "revoked_at": None,
            "created_at": datetime.now(UTC),
        }

        with pytest.raises(DataMappingError) as exc_info:
            RefreshTokenRepository._to_record(mock_row)

        assert "Failed to map database row to RefreshTokenRecord" in exc_info.value.message
        assert exc_info.value.cause is not None

    @pytest.mark.asyncio
    async def test_get_by_token_hash_mapping_error(self):
        """Raise DataMappingError when row mapping fails during fetch."""
        mock_row = {
            "id": "token-123",
            "user_id": "user-456",
            "token_hash": "hash-xyz",
            "expires_at": "invalid",
            "revoked_at": None,
            "created_at": datetime.now(UTC),
        }

        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = mock_row

        repo = RefreshTokenRepository(mock_tx)

        with pytest.raises(DataMappingError) as exc_info:
            await repo.get_by_token_hash("hash-xyz")

        assert (
            exc_info.value.message
            == "Failed to map database row to RefreshTokenRecord"
        )

    @pytest.mark.asyncio
    async def test_to_record_with_revoked_at_success(self):
        """Successfully map a revoked token."""
        now = datetime.now(UTC)
        revoked = now + timedelta(hours=1)
        mock_row = {
            "id": "token-123",
            "user_id": "user-456",
            "token_hash": "hash-xyz",
            "expires_at": now + timedelta(days=7),
            "revoked_at": revoked,
            "created_at": now,
        }

        result = RefreshTokenRepository._to_record(mock_row)

        assert result.id == "token-123"
        assert result.revoked_at == revoked

    @pytest.mark.asyncio
    async def test_to_record_with_iso_string_dates(self):
        """Successfully map a record with ISO format date strings."""
        now = datetime.now(UTC)
        expires = (now + timedelta(days=7)).isoformat()
        created = now.isoformat()

        mock_row = {
            "id": "token-123",
            "user_id": "user-456",
            "token_hash": "hash-xyz",
            "expires_at": expires,
            "revoked_at": None,
            "created_at": created,
        }

        result = RefreshTokenRepository._to_record(mock_row)

        assert result.id == "token-123"
        assert isinstance(result.expires_at, datetime)
        assert isinstance(result.created_at, datetime)
