"""User request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    """Request schema for creating a user."""

    name: str
    email: str


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    name: str
    email: str
