"""Shared form helpers: validation and coercion for admin views."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.admin.resource import FieldType

if TYPE_CHECKING:
    from app.admin.resource import FieldConfig


def validate_form(fields: list[FieldConfig], data: dict[str, str]) -> dict[str, str]:
    """Validate form data against field configs. Return errors dict."""
    errors: dict[str, str] = {}
    for field in fields:
        if field.readonly:
            continue
        value = data.get(field.name, "").strip()

        if field.required and field.field_type != FieldType.BOOLEAN and not value:
            errors[field.name] = "This field is required."
            continue

        if value and field.field_type == FieldType.NUMBER:
            try:
                float(value)
            except ValueError:
                errors[field.name] = "Must be a number."

        if value and field.field_type == FieldType.SELECT and field.choices:
            valid_values = {c[0] for c in field.choices}
            if value not in valid_values:
                errors[field.name] = "Invalid choice."

    return errors


def coerce_form_data(
    fields: list[FieldConfig], raw: dict[str, str]
) -> dict[str, object]:
    """Coerce form string values to appropriate Python types."""
    result: dict[str, object] = {}
    for field in fields:
        if field.readonly:
            continue
        value = raw.get(field.name, "").strip()

        if field.field_type == FieldType.BOOLEAN:
            result[field.name] = field.name in raw
        elif field.field_type == FieldType.NUMBER and value:
            try:
                # Prefer int when possible, fall back to float for values like "1e3"
                result[field.name] = int(value)
            except ValueError:
                result[field.name] = float(value)
        elif value:
            result[field.name] = value
        else:
            result[field.name] = None if not field.required else ""

    return result
