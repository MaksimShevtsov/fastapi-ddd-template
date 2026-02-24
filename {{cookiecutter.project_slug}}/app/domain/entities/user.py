"""UserEntity domain entity (stdlib only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.errors import ValidationError
from app.domain.value_objects.user_id import UserId


@dataclass
class UserEntity:
    """User domain entity with invariant enforcement."""

    id: UserId
    name: str
    email: str
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def create(cls, *, name: str, email: str) -> UserEntity:
        """Factory method to create a new user with invariant validation."""
        cls._validate_name(name)
        cls._validate_email(email)
        return cls(
            id=UserId.generate(),
            name=name,
            email=email,
            created_at=datetime.now(timezone.utc),
        )

    def update_name(self, name: str) -> None:
        """Update the user's name with invariant enforcement."""
        self._validate_name(name)
        self.name = name
        self.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValidationError(code="INVALID_NAME", message="Name must be non-empty")

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email or "@" not in email:
            raise ValidationError(code="INVALID_EMAIL", message="Email must contain @")
