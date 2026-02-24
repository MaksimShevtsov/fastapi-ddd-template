"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request) -> dict:
    """Return service health status."""
    settings = request.app.state.settings
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.1.0",
    }
