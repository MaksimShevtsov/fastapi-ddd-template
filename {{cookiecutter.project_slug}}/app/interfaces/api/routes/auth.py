"""Auth API routes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Request
from fastapi_request_pipeline import RequestContext, flow_dependency

from app.application.bus.command_bus import CommandBus
from app.application.bus.query_bus import QueryBus
from app.application.commands.change_password import ChangePasswordCommand
from app.application.commands.login_user import LoginUserCommand
from app.application.commands.logout_user import LogoutUserCommand
from app.application.commands.refresh_token import RefreshTokenCommand
from app.application.commands.register_user import RegisterUserCommand
from app.application.queries.get_user import GetUserQuery
from app.interfaces.api.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.interfaces.api.schemas.user import UserResponse
from app.interfaces.dependencies.container import (
    get_command_bus,
    get_password_hasher,
    get_query_bus,
    get_token_service,
    get_unit_of_work,
)
from app.interfaces.pipeline.flows import authenticated_flow, public_flow

if TYPE_CHECKING:
    from app.application.services.token_service import TokenService
    from app.application.unit_of_work import UnitOfWork
    from app.domain.services.password_hasher import PasswordHasher

router = APIRouter(tags=["auth"])


@router.post("/auth/register", status_code=201, response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    _ctx: RequestContext = Depends(flow_dependency(public_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """Register a new user and return tokens."""
    command = RegisterUserCommand(name=body.name, email=body.email, password=body.password)
    result = await bus.dispatch(command, uow=uow, password_hasher=password_hasher, token_service=token_service)
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    _ctx: RequestContext = Depends(flow_dependency(public_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """Log in a user and return tokens."""
    command = LoginUserCommand(email=body.email, password=body.password)
    result = await bus.dispatch(command, uow=uow, password_hasher=password_hasher, token_service=token_service)
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    _ctx: RequestContext = Depends(flow_dependency(public_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
    token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """Refresh access token using a refresh token."""
    command = RefreshTokenCommand(refresh_token=body.refresh_token)
    result = await bus.dispatch(command, uow=uow, token_service=token_service)
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    )


@router.post("/auth/logout", status_code=204)
async def logout(
    body: RefreshRequest,
    _ctx: RequestContext = Depends(flow_dependency(public_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
    token_service: TokenService = Depends(get_token_service),
) -> None:
    """Log out by revoking the refresh token."""
    command = LogoutUserCommand(refresh_token=body.refresh_token)
    await bus.dispatch(command, uow=uow, token_service=token_service)


@router.get("/auth/me", response_model=UserResponse)
async def me(
    request: Request,
    ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
    bus: QueryBus = Depends(get_query_bus),
) -> UserResponse:
    """Get the current authenticated user."""
    user_id = ctx.state["user_id"]
    query = GetUserQuery(user_id=user_id)
    result = await bus.dispatch(query)
    return result


@router.post("/auth/change-password", status_code=204)
async def change_password(
    body: ChangePasswordRequest,
    ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> None:
    """Change the authenticated user's password."""
    user_id = ctx.state["user_id"]
    command = ChangePasswordCommand(user_id=user_id, old_password=body.old_password, new_password=body.new_password)
    await bus.dispatch(command, uow=uow, password_hasher=password_hasher)
