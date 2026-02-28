"""Resource edit view: GET+POST /admin/{resource_name}/{record_id}/edit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin, set_flash
from app.admin.views.resource_create import _coerce_form_data, _validate_form

if TYPE_CHECKING:
    from app.admin.site import AdminSite


def build_edit_routes(router: APIRouter, site: AdminSite) -> None:
    """Register resource edit routes on the router."""

    @router.get(
        "/{resource_name}/{record_id}/edit",
        response_class=HTMLResponse,
        response_model=None,
    )
    async def resource_edit_form(
        request: Request, resource_name: str, record_id: str
    ) -> Response:
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

        record = await resource.dao.get(record_id)
        if record is None:
            html = site.render(
                "admin/404.html",
                request,
                admin_user=user,
                message=f"Record '{record_id}' not found.",
                active_nav=resource_name,
            )
            return HTMLResponse(html, status_code=404)

        form_data = {k: str(v) if v is not None else "" for k, v in record.items()}

        html = site.render(
            "admin/form.html",
            request,
            admin_user=user,
            resource=resource,
            form_data=form_data,
            errors={},
            is_edit=True,
            record_id=record_id,
            active_nav=resource_name,
        )
        return HTMLResponse(html)

    @router.post(
        "/{resource_name}/{record_id}/edit",
        response_class=HTMLResponse,
        response_model=None,
    )
    async def resource_edit_submit(
        request: Request, resource_name: str, record_id: str
    ) -> Response:
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
                is_edit=True,
                record_id=record_id,
                active_nav=resource_name,
            )
            return HTMLResponse(html)

        coerced = _coerce_form_data(resource.form_fields, raw_data)
        try:
            await resource.dao.update(record_id, coerced)
            set_flash(request, "success", "Record updated.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/{record_id}",
                status_code=303,
            )
        except Exception as exc:
            set_flash(request, "error", f"Error updating record: {exc}")
            html = site.render(
                "admin/form.html",
                request,
                admin_user=user,
                resource=resource,
                form_data=raw_data,
                errors={},
                is_edit=True,
                record_id=record_id,
                active_nav=resource_name,
            )
            return HTMLResponse(html)
