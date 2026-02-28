"""AdminSite: central registry and router factory for the admin panel."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import AdminAuthProvider, get_flash

if TYPE_CHECKING:
    from app.admin.resource import ResourceAdmin

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STATIC_DIR = Path(__file__).parent / "static"


class AdminSite:
    """Central registry and configuration for the admin panel."""

    def __init__(
        self,
        title: str = "Admin",
        prefix: str = "/admin",
        auth_provider: AdminAuthProvider | None = None,
        session_secret: str = "change-me-in-production",
    ) -> None:
        if not prefix.startswith("/"):
            raise ValueError("prefix must start with '/'")

        self.title = title
        self.prefix = prefix
        self.auth_provider = auth_provider
        self.session_secret = session_secret
        self._resources: dict[str, ResourceAdmin] = {}
        self._env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=True,
        )

    def register(self, resource: ResourceAdmin) -> None:
        """Register a resource with the admin panel."""
        if resource.name in self._resources:
            raise ValueError(f"Resource '{resource.name}' is already registered")
        self._resources[resource.name] = resource

    def get_resources(self) -> list[ResourceAdmin]:
        """Return all registered resources in registration order."""
        return list(self._resources.values())

    def get_resource(self, name: str) -> ResourceAdmin | None:
        """Return a resource by name, or None."""
        return self._resources.get(name)

    def render(self, template_name: str, request: Request, **context: object) -> str:
        """Render a Jinja2 template with common admin context."""
        template = self._env.get_template(template_name)
        flash = get_flash(request)
        return template.render(
            admin_title=self.title,
            admin_prefix=self.prefix,
            admin_resources=self.get_resources(),
            admin_user=context.pop("admin_user", None),
            flash=flash,
            request=request,
            **context,
        )

    def get_router(self) -> APIRouter:
        """Build and return the APIRouter with all admin routes."""
        if not self._resources:
            raise RuntimeError("No resources registered. Call register() first.")

        from app.admin.views.auth import build_auth_routes
        from app.admin.views.dashboard import build_dashboard_routes
        from app.admin.views.resource_create import build_create_routes
        from app.admin.views.resource_delete import build_delete_routes
        from app.admin.views.resource_detail import build_detail_routes
        from app.admin.views.resource_edit import build_edit_routes
        from app.admin.views.resource_list import build_list_routes

        router = APIRouter(prefix=self.prefix)

        build_auth_routes(router, self)
        build_dashboard_routes(router, self)
        build_list_routes(router, self)
        build_create_routes(router, self)
        build_edit_routes(router, self)
        build_delete_routes(router, self)
        build_detail_routes(router, self)

        return router

    def mount(self, app: FastAPI) -> None:
        """Mount admin panel on the FastAPI app.

        Includes the router, mounts static files, and adds SessionMiddleware.
        """
        app.state.admin_site = self
        app.include_router(self.get_router())
        app.mount(
            f"{self.prefix}/static",
            StaticFiles(directory=str(_STATIC_DIR)),
            name="admin-static",
        )
        app.add_middleware(
            SessionMiddleware,
            secret_key=self.session_secret,
            session_cookie="admin_session",
            same_site="lax",
            https_only=False,
        )
