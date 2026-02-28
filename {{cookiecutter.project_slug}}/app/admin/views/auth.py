"""Auth views: login, logout."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import Response

if TYPE_CHECKING:
    from app.admin.site import AdminSite


def build_auth_routes(router: APIRouter, site: AdminSite) -> None:
    """Register login/logout routes on the router."""

    @router.get("/login", response_class=HTMLResponse, response_model=None)
    async def login_page(request: Request) -> Response:
        user_id = request.session.get("admin_user_id")
        if user_id and site.auth_provider:
            user = await site.auth_provider.get_user(user_id)
            if user and user.get("is_admin"):
                return RedirectResponse(url=f"{site.prefix}/", status_code=303)

        html = site.render(
            "admin/login.html",
            request,
            error=None,
            active_nav="",
        )
        return HTMLResponse(html)

    @router.post("/login", response_class=HTMLResponse, response_model=None)
    async def login_submit(request: Request) -> Response:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

        if site.auth_provider:
            user = await site.auth_provider.authenticate(str(username), str(password))
        else:
            user = None

        if user and user.get("is_admin"):
            request.session["admin_user_id"] = user["id"]
            return RedirectResponse(url=f"{site.prefix}/", status_code=303)

        html = site.render(
            "admin/login.html",
            request,
            error="Invalid username or password.",
            active_nav="",
        )
        return HTMLResponse(html)

    @router.get("/logout", response_model=None)
    async def logout(request: Request) -> Response:
        request.session.clear()
        return RedirectResponse(url=f"{site.prefix}/login", status_code=303)
