"""Authentication pipeline stage — JWT Bearer token validation."""

from __future__ import annotations

from fastapi_request_pipeline import ComponentCategory, FlowComponent, RequestContext

from app.application.services.token_service import TokenService
from app.infrastructure.config import Settings


class AuthenticationStage(FlowComponent):
    """Extracts and validates a JWT Bearer token from the Authorization header.

    On success, sets ctx.state["user_id"] and ctx.state["authenticated"] = True.
    Aborts with 401 on missing/invalid token.
    """

    category = ComponentCategory.AUTHENTICATION

    async def resolve(self, ctx: RequestContext) -> None:
        """Authenticate the request via JWT Bearer token."""
        auth_header = ctx.request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            ctx.abort("Missing or invalid Authorization header")
            return

        token = auth_header[7:]  # Strip "Bearer "

        settings: Settings = ctx.request.app.state.settings
        token_service = TokenService(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        try:
            payload = token_service.decode_token(token)
        except Exception:
            ctx.abort("Invalid or expired token")
            return

        if payload.get("type") != "access":
            ctx.abort("Token is not an access token")
            return

        ctx.state["user_id"] = payload["sub"]
        ctx.state["authenticated"] = True
