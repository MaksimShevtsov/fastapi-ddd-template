"""RegisterUserCommand handler."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.application.bus.command_bus import command_handler
from app.application.commands.register_user import RegisterUserCommand
from app.application.dto.auth_dto import AuthTokensDTO
from app.domain.entities.user import UserEntity
from app.domain.errors import ConflictError
from app.domain.interfaces.refresh_token_repository import RefreshTokenRecord

if TYPE_CHECKING:
    from app.application.services.token_service import TokenService
    from app.application.unit_of_work import UnitOfWork
    from app.domain.services.password_hasher import PasswordHasher


@command_handler(RegisterUserCommand)
async def handle_register_user(
    command: RegisterUserCommand,
    *,
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
    token_service: TokenService,
) -> AuthTokensDTO:
    """Register a new user: hash password, check uniqueness, create user, return tokens."""
    async with uow:
        existing = await uow.user_repository.get_by_email(command.email)
        if existing is not None:
            raise ConflictError(code="EMAIL_TAKEN", message="A user with this email already exists")

        password_hash = password_hasher.hash(command.password)
        user = UserEntity.create(name=command.name, email=command.email, password_hash=password_hash)
        await uow.user_repository.save(user)

        user_id = str(user.id_.value)
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
