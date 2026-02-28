"""Resource configuration types for admin panel."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.admin.dao import AdminDAO


class FieldType(str, Enum):
    """HTML input types for admin form fields."""

    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    TEXTAREA = "textarea"


@dataclass(frozen=True)
class FieldConfig:
    """Configuration for a single form field in create/edit views."""

    name: str
    label: str
    field_type: FieldType
    required: bool = True
    choices: list[tuple[str, str]] | None = None
    placeholder: str | None = None
    help_text: str | None = None
    readonly: bool = False


@dataclass(frozen=True)
class ColumnConfig:
    """Configuration for a column in the list view table."""

    name: str
    label: str
    link_to_detail: bool = False


_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class ResourceAdmin:
    """Configuration for a single registered domain resource."""

    name: str
    display_name: str
    dao: AdminDAO
    list_columns: list[ColumnConfig]
    form_fields: list[FieldConfig]
    id_field: str = "id"
    icon: str | None = None
    page_size: int = 25

    def __post_init__(self) -> None:
        if not _SLUG_RE.match(self.name):
            raise ValueError(
                f"Resource name '{self.name}' must be lowercase alphanumeric with hyphens"
            )
        if not self.list_columns:
            raise ValueError("list_columns must not be empty")
        if not self.form_fields:
            raise ValueError("form_fields must not be empty")

        all_field_names = {c.name for c in self.list_columns} | {
            f.name for f in self.form_fields
        }
        if self.id_field not in all_field_names:
            raise ValueError(
                f"id_field '{self.id_field}' must exist in list_columns or form_fields"
            )

        for f in self.form_fields:
            if f.field_type == FieldType.SELECT and not f.choices:
                raise ValueError(f"Select field '{f.name}' must have choices defined")
