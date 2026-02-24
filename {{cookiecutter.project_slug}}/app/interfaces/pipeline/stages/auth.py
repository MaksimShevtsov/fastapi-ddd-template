"""Authentication pipeline stage stub."""

from __future__ import annotations

from fastapi_request_pipeline import ComponentCategory, FlowComponent, RequestContext


class AuthenticationStage(FlowComponent):
    """Authentication stage stub.

    Replace with actual authentication logic (e.g., JWT token validation).
    """

    category = ComponentCategory.AUTHENTICATION

    async def resolve(self, ctx: RequestContext) -> None:
        """Authenticate the request. Override with real logic."""
