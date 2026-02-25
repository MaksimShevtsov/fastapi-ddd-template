"""Bcrypt password hasher implementation."""

from __future__ import annotations

import bcrypt


class BcryptPasswordHasher:
    """Concrete PasswordHasher using bcrypt."""

    def hash(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, password_hash: str) -> bool:
        """Verify a password against a bcrypt hash."""
        return bcrypt.checkpw(password.encode(), password_hash.encode())
