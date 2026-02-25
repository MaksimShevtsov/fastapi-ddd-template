"""RefreshTokenCommand handler."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.application.bus.command_bus import command_handler
from app.application.commands.refresh_token import RefreshTokenCommand
from app.application.dto.auth_dto import AuthTokensDTO
from app.domain.errors import AuthenticationError
from app.domain.interfaces.refresh_token_repository import RefreshTokenRecord

if TYPE_CHECKING:
    from app.application.services.token_service import TokenService
    from app.application.unit_of_work import UnitOfWork


@command_handler(RefreshTokenCommand)
async def handle_refresh_token(
    command: RefreshTokenCommand,
    *,
    uow: UnitOfWork,
    token_service: TokenService,
) -> AuthTokensDTO:
    """Validate refresh token, issue new pair, revoke old."""
    try:
        payload = token_service.decode_token(command.refresh_token)
    except Exception as exc:
        raise AuthenticationError(code="INVALID_TOKEN", message="Invalid or expired refresh token") from exc

    if payload.get("type") != "refresh":
        raise AuthenticationError(code="INVALID_TOKEN", message="Token is not a refresh token")

    token_hash = token_service.hash_token(command.refresh_token)

    async with uow:
        record = await uow.refresh_token_repository.get_by_token_hash(token_hash)
        if record is None or record.revoked_at is not None:
            raise AuthenticationError(code="TOKEN_REVOKED", message="Refresh token has been revoked")

        if record.expires_at < datetime.now(UTC):
            raise AuthenticationError(code="TOKEN_EXPIRED", message="Refresh token has expired")

        # Revoke old refresh token
        await uow.refresh_token_repository.revoke(record.id)

        # Issue new pair
        user_id = payload["sub"]
        access_token = token_service.create_access_token(user_id)
        new_refresh_token, new_token_id, expires_at = token_service.create_refresh_token(user_id)

        await uow.refresh_token_repository.save(
            RefreshTokenRecord(
                id=new_token_id,
                user_id=user_id,
                token_hash=token_service.hash_token(new_refresh_token),
                expires_at=expires_at,
                revoked_at=None,
                created_at=datetime.now(UTC),
            )
        )

    return AuthTokensDTO(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=token_service.access_token_expire_minutes * 60,
    )
