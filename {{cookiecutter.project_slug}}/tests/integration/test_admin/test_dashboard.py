"""Integration tests for admin dashboard (US1)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_redirects_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/admin/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login" in resp.headers["location"]


@pytest.mark.asyncio
async def test_dashboard_renders_with_resource_counts(
    authed_client: AsyncClient,
) -> None:
    resp = await authed_client.get("/admin/")
    assert resp.status_code == 200
    body = resp.text
    assert "Users" in body
    assert "3" in body  # 3 seeded records


@pytest.mark.asyncio
async def test_dashboard_shows_welcome_message(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/")
    assert resp.status_code == 200
    assert "admin" in resp.text


@pytest.mark.asyncio
async def test_dashboard_sidebar_navigation_links(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/")
    assert resp.status_code == 200
    assert "/admin/users/" in resp.text
