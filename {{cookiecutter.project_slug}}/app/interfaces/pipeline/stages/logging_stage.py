"""Logging pipeline stage."""

from __future__ import annotations

import logging

from fastapi_request_pipeline import ComponentCategory, FlowComponent, RequestContext

logger = logging.getLogger(__name__)


class LoggingStage(FlowComponent):
    """Logs request method, path, and user info."""

    category = ComponentCategory.CUSTOM

    async def resolve(self, ctx: RequestContext) -> None:
        """Log the incoming request."""
        user_info = getattr(ctx, "user", None)
        logger.info(
            "Request: %s %s (user=%s)",
            ctx.request.method,
            ctx.request.url.path,
            user_info,
        )
