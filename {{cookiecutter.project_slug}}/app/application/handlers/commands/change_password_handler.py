"""ChangePasswordCommand handler."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.application.bus.command_bus import command_handler
from app.application.commands.change_password import ChangePasswordCommand
from app.domain.errors import AuthenticationError, NotFoundError, ValidationError
from app.domain.value_objects.user_id import UserId

if TYPE_CHECKING:
    from app.application.unit_of_work import UnitOfWork
    from app.domain.services.password_hasher import PasswordHasher


@command_handler(ChangePasswordCommand)
async def handle_change_password(
    command: ChangePasswordCommand,
    *,
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
) -> None:
    """Verify old password, update to new password."""
    try:
        parsed_user_id = uuid.UUID(command.user_id)
    except ValueError:
        raise ValidationError(code="INVALID_USER_ID", message="Malformed user ID")

    async with uow:
        user = await uow.user_repository.get_by_id(UserId(value=parsed_user_id))
        if user is None:
            raise NotFoundError(code="USER_NOT_FOUND", message="User not found")

        if not password_hasher.verify(command.old_password, user.password_hash):
            raise AuthenticationError(code="INVALID_PASSWORD", message="Current password is incorrect")

        user.update_password(password_hasher.hash(command.new_password))
        await uow.user_repository.save(user)
