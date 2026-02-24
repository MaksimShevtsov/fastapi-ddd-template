"""Flow compositions for request pipeline."""

from __future__ import annotations

from fastapi_request_pipeline import Flow

from app.interfaces.pipeline.stages.auth import AuthenticationStage
from app.interfaces.pipeline.stages.logging_stage import LoggingStage
from app.interfaces.pipeline.stages.permission import PermissionStage

public_flow = Flow(
    LoggingStage(),
)

authenticated_flow = Flow(
    AuthenticationStage(),
    PermissionStage(),
    LoggingStage(),
)
