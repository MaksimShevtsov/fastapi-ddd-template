"""FastAPI application factory with lifespan and exception handlers."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_request_pipeline import FlowAbort

from app.domain.errors import DomainError
from app.infrastructure.config import Settings
from app.infrastructure.db.connection import create_engine
from app.infrastructure.logging import setup_logging
from app.interfaces.api.routes.health import router as health_router
from app.interfaces.api.routes.users import router as users_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: initialize and shutdown resources."""
    settings = Settings()
    setup_logging(settings)
    engine = create_engine(settings)
    app.state.settings = settings
    app.state.engine = engine
    logger.info("Application started", extra={"service": settings.app_name})
    yield
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(users_router, prefix="/api/v1")

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(FlowAbort)
    async def flow_abort_handler(_request: Request, exc: FlowAbort) -> JSONResponse:
        status_map = {
            "AuthenticationFailed": 401,
            "PermissionDenied": 403,
            "Throttled": 429,
        }
        exc_name = type(exc).__name__
        status_code = status_map.get(exc_name, 400)
        code = exc_name.upper()
        return JSONResponse(
            status_code=status_code,
            content={"error": {"code": code, "message": str(exc), "details": {}}},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred", "details": {}}},
        )

    return app


app = create_app()
