"""JWT token service for creating and decoding tokens."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.domain.errors import AuthenticationError


class TokenService:
    """Creates and decodes JWT access and refresh tokens."""

    def __init__(
        self,
        *,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    @property
    def access_token_expire_minutes(self) -> int:
        return self._access_token_expire_minutes

    def create_access_token(self, user_id: str) -> str:
        """Create a short-lived access token."""
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self._access_token_expire_minutes),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: str) -> tuple[str, str, datetime]:
        """Create a long-lived refresh token.

        Returns (encoded_token, token_id, expires_at).
        """
        now = datetime.now(UTC)
        token_id = str(uuid.uuid4())
        expires_at = now + timedelta(days=self._refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": expires_at,
            "jti": token_id,
        }
        encoded = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return encoded, token_id, expires_at

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token.

        Raises AuthenticationError if token is invalid, expired, or malformed.
        """
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as exc:
            raise AuthenticationError(
                code="INVALID_TOKEN", message="Token is invalid or expired"
            ) from exc

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage (refresh tokens are stored hashed)."""
        return hashlib.sha256(token.encode()).hexdigest()
