"""Error response schema for the API envelope."""

from __future__ import annotations

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail inside the error envelope."""

    code: str
    message: str
    details: dict = {}


class ErrorResponse(BaseModel):
    """Standardized error response envelope."""

    error: ErrorDetail
