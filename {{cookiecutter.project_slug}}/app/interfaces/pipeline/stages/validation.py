"""Validation pipeline stage stub."""

from __future__ import annotations

from fastapi_request_pipeline import ComponentCategory, FlowComponent, RequestContext


class ValidationStage(FlowComponent):
    """Request validation stage stub.

    Replace with custom validation logic beyond Pydantic schema validation.
    """

    category = ComponentCategory.CUSTOM

    async def resolve(self, ctx: RequestContext) -> None:
        """Validate the request. Override with real logic."""
