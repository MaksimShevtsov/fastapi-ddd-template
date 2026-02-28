"""FastAPI application factory with lifespan and exception handlers."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_request_pipeline import FlowAbort

import app.application.handlers.commands.change_password_handler  # noqa: F401
import app.application.handlers.commands.create_user_handler  # noqa: F401
import app.application.handlers.commands.login_user_handler  # noqa: F401
import app.application.handlers.commands.logout_user_handler  # noqa: F401
import app.application.handlers.commands.refresh_token_handler  # noqa: F401
import app.application.handlers.commands.register_user_handler  # noqa: F401
import app.application.handlers.queries.get_user_handler  # noqa: F401
from app.application.bus.command_bus import DuplicateHandlerError, HandlerNotFoundError
from app.domain.errors import DomainError
from app.infrastructure.config import Settings
from app.infrastructure.db.connection import create_engine
from app.infrastructure.errors import InfrastructureError
from app.infrastructure.logging import setup_logging
from app.interfaces.api.routes.auth import router as auth_router
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
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")

    # Admin panel — only mounted when ADMIN_ENABLED=true in environment
    settings = Settings()
    if settings.admin_enabled:
        from app.admin.site import AdminSite
        from app.admin_resources.auth import FakeAdminAuthProvider
        from app.admin_resources.users import create_user_resource

        admin = AdminSite(
            title="{{ cookiecutter.project_name }} Admin",
            auth_provider=FakeAdminAuthProvider(),
            session_secret=settings.admin_session_secret,
            https_only=settings.admin_https_only,
        )
        admin.register(create_user_resource())
        admin.mount(app)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors with custom envelope."""
        details = {".".join(str(p) for p in e["loc"]): e["msg"] for e in exc.errors()}
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": details,
                }
            },
        )

    @app.exception_handler(HandlerNotFoundError)
    async def handler_not_found_error_handler(
        _request: Request, exc: HandlerNotFoundError
    ) -> JSONResponse:
        """Handle missing command handlers (programming error)."""
        logger.error("Handler not found (programming error)", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )

    @app.exception_handler(DuplicateHandlerError)
    async def duplicate_handler_error_handler(
        _request: Request, exc: DuplicateHandlerError
    ) -> JSONResponse:
        """Handle duplicate handler registrations (programming error)."""
        logger.error("Duplicate handler registered (programming error)", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )

    @app.exception_handler(InfrastructureError)
    async def infrastructure_error_handler(
        _request: Request, exc: InfrastructureError
    ) -> JSONResponse:
        """Handle infrastructure errors (DB, mapping, etc.)."""
        logger.exception("Infrastructure error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        """Handle domain errors with custom envelope and status codes."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(FlowAbort)
    async def flow_abort_handler(_request: Request, exc: FlowAbort) -> JSONResponse:
        """Handle request pipeline abort (auth, permission, throttle)."""
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
        """Catch-all for truly unexpected exceptions."""
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )

    return app


app = create_app()
