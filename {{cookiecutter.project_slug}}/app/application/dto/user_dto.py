"""UserDTO for inter-layer communication."""

from __future__ import annotations

from pydantic import BaseModel


class UserDTO(BaseModel):
    """Data transfer object for user data between layers."""

    id: str
    name: str
    email: str
