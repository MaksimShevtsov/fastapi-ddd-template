"""Base ValueObject class for domain value objects."""

from dataclasses import dataclass, fields
from typing import Any, Self


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    """
    Base class for domain value objects.
    - Immutability enforced by `frozen=True`.
    - Equality and hashing derived from all fields by default.
    - Subclasses must also be decorated with `@dataclass(frozen=True, slots=True, repr=False)`.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("Base ValueObject cannot be instantiated directly.")
        return object.__new__(cls)

    def __repr__(self) -> str:
        field_str = ", ".join(
            f"{f.name}={getattr(self, f.name)!r}" for f in fields(self)
        )
        return f"{type(self).__name__}({field_str})"
