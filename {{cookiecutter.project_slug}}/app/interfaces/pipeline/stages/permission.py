"""Authorization pipeline stage stub."""

from __future__ import annotations

from fastapi_request_pipeline import ComponentCategory, FlowComponent, RequestContext


class PermissionStage(FlowComponent):
    """Authorization stage stub.

    Replace with actual permission checking logic.
    """

    category = ComponentCategory.PERMISSION

    async def resolve(self, ctx: RequestContext) -> None:
        """Check permissions. Override with real logic."""
