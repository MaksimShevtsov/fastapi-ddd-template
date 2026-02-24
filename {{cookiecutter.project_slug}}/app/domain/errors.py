"""Domain error hierarchy.

All domain errors inherit from DomainError and carry a machine-readable code,
human-readable message, optional details dict, and HTTP status code.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base domain error."""

    def __init__(
        self,
        *,
        code: str = "DOMAIN_ERROR",
        message: str = "A domain error occurred",
        details: dict | None = None,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(DomainError):
    """Entity not found."""

    def __init__(
        self,
        *,
        code: str = "NOT_FOUND",
        message: str = "Resource not found",
        details: dict | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, status_code=404)


class ConflictError(DomainError):
    """Duplicate or conflicting state."""

    def __init__(
        self,
        *,
        code: str = "CONFLICT",
        message: str = "Resource conflict",
        details: dict | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, status_code=409)


class ValidationError(DomainError):
    """Business rule / invariant violation."""

    def __init__(
        self,
        *,
        code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
        details: dict | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, status_code=422)
