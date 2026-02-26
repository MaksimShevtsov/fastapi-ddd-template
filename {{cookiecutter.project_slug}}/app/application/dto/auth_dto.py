"""Auth DTOs for inter-layer communication."""

from __future__ import annotations

from pydantic import BaseModel


class AuthTokensDTO(BaseModel):
    """Data transfer object for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
