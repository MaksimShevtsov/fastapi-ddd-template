"""CreateUserCommand handler."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.bus.command_bus import command_handler
from app.application.commands.create_user import CreateUserCommand
from app.application.dto.user_dto import UserDTO
from app.domain.entities.user import UserEntity

if TYPE_CHECKING:
    from app.application.unit_of_work import UnitOfWork


@command_handler(CreateUserCommand)
async def handle_create_user(command: CreateUserCommand, *, uow: UnitOfWork) -> UserDTO:
    """Handle user creation: validate, persist, return DTO."""
    user = UserEntity.create(name=command.name, email=command.email, password_hash="")
    async with uow:
        await uow.user_repository.save(user)
    return UserDTO(id=str(user.id_.value), name=user.name, email=user.email)
