"""Resource create view: GET+POST /admin/{resource_name}/create."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin, set_flash
from app.admin.resource import FieldType

if TYPE_CHECKING:
    from app.admin.resource import FieldConfig
    from app.admin.site import AdminSite


def _validate_form(fields: list[FieldConfig], data: dict[str, str]) -> dict[str, str]:
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


def _coerce_form_data(
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
            result[field.name] = float(value) if "." in value else int(value)
        elif value:
            result[field.name] = value
        else:
            result[field.name] = None if not field.required else ""

    return result


def build_create_routes(router: APIRouter, site: AdminSite) -> None:
    """Register resource create routes on the router."""

    @router.get(
        "/{resource_name}/create", response_class=HTMLResponse, response_model=None
    )
    async def resource_create_form(request: Request, resource_name: str) -> Response:
        user = await require_admin(request)
        if isinstance(user, RedirectResponse):
            return user

        resource = site.get_resource(resource_name)
        if not resource:
            html = site.render(
                "admin/404.html",
                request,
                admin_user=user,
                message=f"Resource '{resource_name}' not found.",
                active_nav="",
            )
            return HTMLResponse(html, status_code=404)

        html = site.render(
            "admin/form.html",
            request,
            admin_user=user,
            resource=resource,
            form_data={},
            errors={},
            is_edit=False,
            active_nav=resource_name,
        )
        return HTMLResponse(html)

    @router.post(
        "/{resource_name}/create", response_class=HTMLResponse, response_model=None
    )
    async def resource_create_submit(request: Request, resource_name: str) -> Response:
        user = await require_admin(request)
        if isinstance(user, RedirectResponse):
            return user

        resource = site.get_resource(resource_name)
        if not resource:
            html = site.render(
                "admin/404.html",
                request,
                admin_user=user,
                message=f"Resource '{resource_name}' not found.",
                active_nav="",
            )
            return HTMLResponse(html, status_code=404)

        form = await request.form()
        raw_data = {key: str(form[key]) for key in form}

        errors = _validate_form(resource.form_fields, raw_data)
        if errors:
            html = site.render(
                "admin/form.html",
                request,
                admin_user=user,
                resource=resource,
                form_data=raw_data,
                errors=errors,
                is_edit=False,
                active_nav=resource_name,
            )
            return HTMLResponse(html)

        coerced = _coerce_form_data(resource.form_fields, raw_data)
        try:
            await resource.dao.create(coerced)
            set_flash(request, "success", "Record created.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/", status_code=303
            )
        except Exception as exc:
            set_flash(request, "error", f"Error creating record: {exc}")
            html = site.render(
                "admin/form.html",
                request,
                admin_user=user,
                resource=resource,
                form_data=raw_data,
                errors={},
                is_edit=False,
                active_nav=resource_name,
            )
            return HTMLResponse(html)
