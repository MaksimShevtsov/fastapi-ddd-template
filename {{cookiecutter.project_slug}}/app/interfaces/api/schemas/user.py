"""User request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    """Request schema for creating a user."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    name: str
    email: str
