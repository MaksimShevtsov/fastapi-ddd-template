"""Infrastructure error hierarchy for system/db-level faults.

These are NOT domain errors — they signal a system or infrastructure fault,
not a business rule violation.
"""

from __future__ import annotations


class InfrastructureError(Exception):
    """Base infrastructure error."""

    def __init__(self, *, message: str = "An infrastructure error occurred") -> None:
        self.message = message
        super().__init__(message)


class DatabaseError(InfrastructureError):
    """Wraps database driver errors (connection, constraint, etc.)."""

    def __init__(
        self, *, message: str = "Database operation failed", cause: Exception | None = None
    ) -> None:
        self.message = message
        self.cause = cause
        super().__init__(message=message)


class DataMappingError(InfrastructureError):
    """Malformed or unexpected data structure from database row mapper."""

    def __init__(
        self, *, message: str = "Data mapping failed", cause: Exception | None = None
    ) -> None:
        self.message = message
        self.cause = cause
        super().__init__(message=message)
