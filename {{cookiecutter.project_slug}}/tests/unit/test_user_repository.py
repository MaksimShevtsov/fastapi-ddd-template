"""Tests for UserRepository error handling."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.entities.user import UserEntity
from app.domain.value_objects.user_id import UserId
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.errors import DatabaseError, DataMappingError


class TestUserRepositoryGetById:
    """Test UserRepository.get_by_id()."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self):
        """Successfully fetch a user by ID."""
        user_id = UserId(value=uuid.uuid4())
        mock_row = {
            "id": user_id.value,
            "name": "John Doe",
            "email": "john@example.com",
            "password_hash": "hash123",
            "created_at": datetime.now(UTC),
            "updated_at": None,
        }

        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = mock_row

        repo = UserRepository(mock_tx)
        result = await repo.get_by_id(user_id)

        assert result is not None
        assert result.name == "John Doe"
        assert result.email == "john@example.com"
        mock_tx.fetch_one.assert_called_once_with(
            "users.get_by_id", {"id": str(user_id.value)}
        )

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Return None when user not found."""
        user_id = UserId(value=uuid.uuid4())

        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = None

        repo = UserRepository(mock_tx)
        result = await repo.get_by_id(user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_database_error(self):
        """Raise DatabaseError when database operation fails."""
        user_id = UserId(value=uuid.uuid4())

        mock_tx = AsyncMock()
        mock_tx.fetch_one.side_effect = Exception("Connection lost")

        repo = UserRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.get_by_id(user_id)

        assert exc_info.value.message == "Failed to fetch user by ID"
        assert exc_info.value.cause is not None
        assert str(exc_info.value.cause) == "Connection lost"


class TestUserRepositoryGetByEmail:
    """Test UserRepository.get_by_email()."""

    @pytest.mark.asyncio
    async def test_get_by_email_success(self):
        """Successfully fetch a user by email."""
        mock_row = {
            "id": uuid.uuid4(),
            "name": "Jane Smith",
            "email": "jane@example.com",
            "password_hash": "hash456",
            "created_at": datetime.now(UTC),
            "updated_at": None,
        }

        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = mock_row

        repo = UserRepository(mock_tx)
        result = await repo.get_by_email("jane@example.com")

        assert result is not None
        assert result.name == "Jane Smith"
        mock_tx.fetch_one.assert_called_once_with(
            "users.get_by_email", {"email": "jane@example.com"}
        )

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self):
        """Return None when email not found."""
        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = None

        repo = UserRepository(mock_tx)
        result = await repo.get_by_email("notfound@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_database_error(self):
        """Raise DatabaseError when database operation fails."""
        mock_tx = AsyncMock()
        mock_tx.fetch_one.side_effect = Exception("DB timeout")

        repo = UserRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.get_by_email("test@example.com")

        assert exc_info.value.message == "Failed to fetch user by email"
        assert str(exc_info.value.cause) == "DB timeout"


class TestUserRepositorySave:
    """Test UserRepository.save()."""

    @pytest.mark.asyncio
    async def test_save_success(self):
        """Successfully save a user."""
        user = UserEntity.create(
            name="Bob Johnson",
            email="bob@example.com",
            password_hash="hash789",
        )

        mock_tx = AsyncMock()
        repo = UserRepository(mock_tx)
        await repo.save(user)

        mock_tx.execute.assert_called_once()
        call_args = mock_tx.execute.call_args
        assert call_args[0][0] == "users.insert"
        assert call_args[0][1]["name"] == "Bob Johnson"
        assert call_args[0][1]["email"] == "bob@example.com"

    @pytest.mark.asyncio
    async def test_save_database_error(self):
        """Raise DatabaseError when save fails."""
        user = UserEntity.create(
            name="Alice",
            email="alice@example.com",
            password_hash="hash000",
        )

        mock_tx = AsyncMock()
        mock_tx.execute.side_effect = Exception("Unique constraint violation")

        repo = UserRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.save(user)

        assert exc_info.value.message == "Failed to save user"
        assert "Unique constraint violation" in str(exc_info.value.cause)


class TestUserRepositoryListAll:
    """Test UserRepository.list_all()."""

    @pytest.mark.asyncio
    async def test_list_all_success(self):
        """Successfully fetch all users."""
        mock_rows = [
            {
                "id": uuid.uuid4(),
                "name": "User 1",
                "email": "user1@example.com",
                "password_hash": "hash1",
                "created_at": datetime.now(UTC),
                "updated_at": None,
            },
            {
                "id": uuid.uuid4(),
                "name": "User 2",
                "email": "user2@example.com",
                "password_hash": "hash2",
                "created_at": datetime.now(UTC),
                "updated_at": None,
            },
        ]

        mock_tx = AsyncMock()
        mock_tx.fetch_all.return_value = mock_rows

        repo = UserRepository(mock_tx)
        results = await repo.list_all()

        assert len(results) == 2
        assert results[0].name == "User 1"
        assert results[1].name == "User 2"

    @pytest.mark.asyncio
    async def test_list_all_empty(self):
        """Return empty list when no users exist."""
        mock_tx = AsyncMock()
        mock_tx.fetch_all.return_value = []

        repo = UserRepository(mock_tx)
        results = await repo.list_all()

        assert results == []

    @pytest.mark.asyncio
    async def test_list_all_database_error(self):
        """Raise DatabaseError when fetch fails."""
        mock_tx = AsyncMock()
        mock_tx.fetch_all.side_effect = Exception("Database offline")

        repo = UserRepository(mock_tx)

        with pytest.raises(DatabaseError) as exc_info:
            await repo.list_all()

        assert exc_info.value.message == "Failed to fetch all users"
        assert str(exc_info.value.cause) == "Database offline"


class TestUserRepositoryDataMapping:
    """Test UserRepository data mapping error handling."""

    @pytest.mark.asyncio
    async def test_to_entity_mapping_error_invalid_uuid(self):
        """Raise DataMappingError when UUID is invalid."""
        mock_row = {
            "id": "invalid-uuid",
            "name": "Test",
            "email": "test@example.com",
            "password_hash": "hash",
            "created_at": datetime.now(UTC),
            "updated_at": None,
        }

        with pytest.raises(DataMappingError) as exc_info:
            UserRepository._to_entity(mock_row)

        assert "Failed to map database row to UserEntity" in exc_info.value.message
        assert exc_info.value.cause is not None

    @pytest.mark.asyncio
    async def test_to_entity_mapping_error_missing_field(self):
        """Raise DataMappingError when required field is missing."""
        mock_row = {
            "id": uuid.uuid4(),
            "name": "Test",
            # Missing 'email' field
            "password_hash": "hash",
            "created_at": datetime.now(UTC),
        }

        with pytest.raises(DataMappingError) as exc_info:
            UserRepository._to_entity(mock_row)

        assert "Failed to map database row to UserEntity" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_to_entity_mapping_error_invalid_datetime(self):
        """Raise DataMappingError when datetime is invalid."""
        mock_row = {
            "id": uuid.uuid4(),
            "name": "Test",
            "email": "test@example.com",
            "password_hash": "hash",
            "created_at": "not-a-datetime",
            "updated_at": None,
        }

        with pytest.raises(DataMappingError) as exc_info:
            UserRepository._to_entity(mock_row)

        assert "Failed to map database row to UserEntity" in exc_info.value.message
        assert exc_info.value.cause is not None

    @pytest.mark.asyncio
    async def test_get_by_id_mapping_error(self):
        """Raise DataMappingError when row mapping fails during fetch."""
        user_id = UserId(value=uuid.uuid4())
        mock_row = {
            "id": "invalid",
            "name": "Test",
            "email": "test@example.com",
            "password_hash": "hash",
            "created_at": datetime.now(UTC),
        }

        mock_tx = AsyncMock()
        mock_tx.fetch_one.return_value = mock_row

        repo = UserRepository(mock_tx)

        with pytest.raises(DataMappingError) as exc_info:
            await repo.get_by_id(user_id)

        assert exc_info.value.message == "Failed to map database row to UserEntity"
