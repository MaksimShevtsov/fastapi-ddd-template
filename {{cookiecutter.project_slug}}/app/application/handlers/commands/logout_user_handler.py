"""LogoutUserCommand handler."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.bus.command_bus import command_handler
from app.application.commands.logout_user import LogoutUserCommand

if TYPE_CHECKING:
    from app.application.services.token_service import TokenService
    from app.application.unit_of_work import UnitOfWork


@command_handler(LogoutUserCommand)
async def handle_logout_user(
    command: LogoutUserCommand,
    *,
    uow: UnitOfWork,
    token_service: TokenService,
) -> None:
    """Revoke the refresh token to log out."""
    token_hash = token_service.hash_token(command.refresh_token)

    async with uow:
        record = await uow.refresh_token_repository.get_by_token_hash(token_hash)
        if record is not None and record.revoked_at is None:
            await uow.refresh_token_repository.revoke(record.id)
