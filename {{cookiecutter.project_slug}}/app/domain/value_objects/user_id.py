"""UserId value object."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    """Immutable identifier for a User entity."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> UserId:
        """Generate a new unique UserId."""
        return cls(value=uuid.uuid4())

    def __str__(self) -> str:
        return str(self.value)
