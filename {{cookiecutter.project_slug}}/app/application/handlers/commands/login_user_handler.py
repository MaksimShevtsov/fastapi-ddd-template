"""LoginUserCommand handler."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.application.bus.command_bus import command_handler
from app.application.commands.login_user import LoginUserCommand
from app.application.dto.auth_dto import AuthTokensDTO
from app.domain.errors import AuthenticationError
from app.domain.interfaces.refresh_token_repository import RefreshTokenRecord

if TYPE_CHECKING:
    from app.application.services.token_service import TokenService
    from app.application.unit_of_work import UnitOfWork
    from app.domain.services.password_hasher import PasswordHasher


@command_handler(LoginUserCommand)
async def handle_login_user(
    command: LoginUserCommand,
    *,
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
    token_service: TokenService,
) -> AuthTokensDTO:
    """Authenticate user by email/password, return tokens."""
    async with uow:
        user = await uow.user_repository.get_by_email(command.email)
        if user is None or not password_hasher.verify(command.password, user.password_hash):
            raise AuthenticationError(code="INVALID_CREDENTIALS", message="Invalid email or password")

        user_id = str(user.id)
        access_token = token_service.create_access_token(user_id)
        refresh_token, token_id, expires_at = token_service.create_refresh_token(user_id)

        await uow.refresh_token_repository.save(
            RefreshTokenRecord(
                id=token_id,
                user_id=user_id,
                token_hash=token_service.hash_token(refresh_token),
                expires_at=expires_at,
                revoked_at=None,
                created_at=datetime.now(UTC),
            )
        )

    return AuthTokensDTO(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=token_service.access_token_expire_minutes * 60,
    )
