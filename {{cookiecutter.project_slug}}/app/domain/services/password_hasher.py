"""Domain service interface for password hashing."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class PasswordHasher(Protocol):
    """Protocol for password hashing. Keeps bcrypt out of the domain layer."""

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...
