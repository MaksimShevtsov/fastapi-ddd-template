"""QueryBus with decorator-based handler registration."""

from __future__ import annotations

from typing import Any, Callable


class HandlerNotFoundError(Exception):
    """Raised when no handler is registered for a query type."""

    def __init__(self, query_type: type) -> None:
        super().__init__(f"No handler registered for {query_type.__name__}")


class DuplicateHandlerError(Exception):
    """Raised when a handler is already registered for a query type."""

    def __init__(self, query_type: type) -> None:
        super().__init__(f"Handler already registered for {query_type.__name__}")


class QueryBus:
    """Dispatches queries to their registered handlers."""

    _handlers: dict[type, Callable[..., Any]] = {}

    @classmethod
    def handler(cls, query_type: type) -> Callable[..., Any]:
        """Decorator to register a query handler."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if query_type in cls._handlers:
                raise DuplicateHandlerError(query_type)
            cls._handlers[query_type] = func
            return func

        return decorator

    async def dispatch(self, query: Any, **kwargs: Any) -> Any:
        """Dispatch a query to its registered handler."""
        handler = self._handlers.get(type(query))
        if handler is None:
            raise HandlerNotFoundError(type(query))
        return await handler(query, **kwargs)


query_handler = QueryBus.handler
