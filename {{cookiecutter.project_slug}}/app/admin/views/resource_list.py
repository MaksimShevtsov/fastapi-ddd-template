"""Resource list view: GET /admin/{resource_name}/."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

from app.admin.auth import require_admin
from app.admin.utils import compute_pagination

if TYPE_CHECKING:
    from app.admin.site import AdminSite


def build_list_routes(router: APIRouter, site: AdminSite) -> None:
    """Register resource list route on the router."""

    @router.get("/{resource_name}/", response_class=HTMLResponse, response_model=None)
    async def resource_list(request: Request, resource_name: str) -> Response:
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

        page_param = request.query_params.get("page", "1")
        try:
            page = int(page_param)
        except (TypeError, ValueError):
            page = 1
        if page < 1:
            page = 1
        search = request.query_params.get("search") or None

        offset = (page - 1) * resource.page_size
        items, total_count = await resource.dao.list(offset, resource.page_size, search)

        pagination = compute_pagination(page, resource.page_size, total_count)

        html = site.render(
            "admin/list.html",
            request,
            admin_user=user,
            resource=resource,
            items=items,
            page=page,
            total_pages=pagination["total_pages"],
            total_count=total_count,
            search=search or "",
            has_prev=pagination["has_prev"],
            has_next=pagination["has_next"],
            active_nav=resource_name,
        )
        return HTMLResponse(html)
