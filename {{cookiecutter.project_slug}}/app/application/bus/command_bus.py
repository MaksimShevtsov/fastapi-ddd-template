"""CommandBus with decorator-based handler registration."""

from __future__ import annotations

from typing import Any, Callable


class HandlerNotFoundError(Exception):
    """Raised when no handler is registered for a command type."""

    def __init__(self, command_type: type) -> None:
        super().__init__(f"No handler registered for {command_type.__name__}")


class DuplicateHandlerError(Exception):
    """Raised when a handler is already registered for a command type."""

    def __init__(self, command_type: type) -> None:
        super().__init__(f"Handler already registered for {command_type.__name__}")


class CommandBus:
    """Dispatches commands to their registered handlers."""

    _handlers: dict[type, Callable[..., Any]] = {}

    @classmethod
    def handler(cls, command_type: type) -> Callable[..., Any]:
        """Decorator to register a command handler."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if command_type in cls._handlers:
                raise DuplicateHandlerError(command_type)
            cls._handlers[command_type] = func
            return func

        return decorator

    async def dispatch(self, command: Any, **kwargs: Any) -> Any:
        """Dispatch a command to its registered handler."""
        handler = self._handlers.get(type(command))
        if handler is None:
            raise HandlerNotFoundError(type(command))
        return await handler(command, **kwargs)


command_handler = CommandBus.handler
