"""Resource detail view: GET /admin/{resource_name}/{record_id}."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin

if TYPE_CHECKING:
    from app.admin.site import AdminSite


def build_detail_routes(router: APIRouter, site: AdminSite) -> None:
    """Register resource detail route on the router."""

    @router.get(
        "/{resource_name}/{record_id}", response_class=HTMLResponse, response_model=None
    )
    async def resource_detail(
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
            "admin/detail.html",
            request,
            admin_user=user,
            resource=resource,
            record=record,
            active_nav=resource_name,
        )
        return HTMLResponse(html)
