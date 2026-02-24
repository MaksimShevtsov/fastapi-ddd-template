"""User API routes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi_request_pipeline import RequestContext, flow_dependency

from app.application.bus.command_bus import CommandBus
from app.application.bus.query_bus import QueryBus
from app.application.commands.create_user import CreateUserCommand
from app.application.queries.get_user import GetUserQuery
from app.interfaces.api.schemas.user import CreateUserRequest, UserResponse
from app.interfaces.dependencies.container import get_command_bus, get_query_bus, get_unit_of_work
from app.interfaces.pipeline.flows import authenticated_flow

if TYPE_CHECKING:
    from app.application.unit_of_work import UnitOfWork

router = APIRouter(tags=["users"])


@router.post("/users", status_code=201, response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> UserResponse:
    """Create a new user."""
    command = CreateUserCommand(name=request.name, email=request.email)
    result = await bus.dispatch(command, uow=uow)
    return UserResponse(id=result.id, name=result.name, email=result.email)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
    bus: QueryBus = Depends(get_query_bus),
) -> UserResponse:
    """Get a user by ID."""
    query = GetUserQuery(user_id=user_id)
    result = await bus.dispatch(query)
    return result
