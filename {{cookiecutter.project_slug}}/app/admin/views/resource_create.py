"""Resource create view: GET+POST /admin/{resource_name}/create."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin, set_flash, validate_csrf
from app.admin.views.forms import coerce_form_data, validate_form

if TYPE_CHECKING:
    from app.admin.site import AdminSite

logger = logging.getLogger(__name__)


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

        if not validate_csrf(request, raw_data.get("csrf_token")):
            set_flash(request, "error", "Invalid or missing CSRF token.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/create", status_code=303
            )

        errors = validate_form(resource.form_fields, raw_data)
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

        coerced = coerce_form_data(resource.form_fields, raw_data)
        try:
            await resource.dao.create(coerced)
            set_flash(request, "success", "Record created.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/", status_code=303
            )
        except Exception:
            logger.exception("Error creating record for resource '%s'", resource_name)
            set_flash(request, "error", "An error occurred while creating the record.")
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
