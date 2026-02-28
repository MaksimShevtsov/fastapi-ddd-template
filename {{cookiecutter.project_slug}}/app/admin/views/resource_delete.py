"""Resource delete view: GET+POST /admin/{resource_name}/{record_id}/delete."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin, set_flash, validate_csrf

if TYPE_CHECKING:
    from app.admin.site import AdminSite

logger = logging.getLogger(__name__)


def build_delete_routes(router: APIRouter, site: AdminSite) -> None:
    """Register resource delete routes on the router."""

    @router.get(
        "/{resource_name}/{record_id}/delete",
        response_class=HTMLResponse,
        response_model=None,
    )
    async def resource_delete_confirm(
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

        html = site.render(
            "admin/delete_confirm.html",
            request,
            admin_user=user,
            resource=resource,
            record=record,
            record_id=record_id,
            active_nav=resource_name,
        )
        return HTMLResponse(html)

    @router.post("/{resource_name}/{record_id}/delete", response_model=None)
    async def resource_delete_submit(
        request: Request, resource_name: str, record_id: str
    ) -> Response:
        user = await require_admin(request)
        if isinstance(user, RedirectResponse):
            return user

        resource = site.get_resource(resource_name)
        if not resource:
            set_flash(request, "error", "Resource not found.")
            return RedirectResponse(url=f"{site.prefix}/", status_code=303)

        form = await request.form()
        submitted_token = str(form.get("csrf_token", ""))
        if not validate_csrf(request, submitted_token):
            set_flash(request, "error", "Invalid or missing CSRF token.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/{record_id}/delete", status_code=303
            )

        try:
            await resource.dao.delete(record_id)
            set_flash(request, "success", "Record deleted.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/", status_code=303
            )
        except Exception:
            logger.exception(
                "Error deleting record '%s' for resource '%s'", record_id, resource_name
            )
            set_flash(request, "error", "An error occurred while deleting the record.")
            return RedirectResponse(
                url=f"{site.prefix}/{resource_name}/{record_id}",
                status_code=303,
            )
