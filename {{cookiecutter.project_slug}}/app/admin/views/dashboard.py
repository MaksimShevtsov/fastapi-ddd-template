"""Dashboard view: GET /admin/."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin

if TYPE_CHECKING:
    from app.admin.site import AdminSite


def build_dashboard_routes(router: APIRouter, site: AdminSite) -> None:
    """Register dashboard route on the router."""

    @router.get("/", response_class=HTMLResponse, response_model=None)
    async def dashboard(request: Request) -> Response:
        user = await require_admin(request)
        if isinstance(user, RedirectResponse):
            return user

        resource_counts = []
        for resource in site.get_resources():
            _, total = await resource.dao.list(0, 0)
            resource_counts.append(
                {
                    "name": resource.name,
                    "display_name": resource.display_name,
                    "count": total,
                    "icon": resource.icon,
                }
            )

        html = site.render(
            "admin/dashboard.html",
            request,
            admin_user=user,
            resources=resource_counts,
            active_nav="dashboard",
        )
        return HTMLResponse(html)
