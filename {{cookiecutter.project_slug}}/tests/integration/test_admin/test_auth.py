"""Integration tests for admin authentication (US5)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthenticated_redirect(client: AsyncClient) -> None:
    resp = await client.get("/admin/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login" in resp.headers["location"]


@pytest.mark.asyncio
async def test_login_page_renders(client: AsyncClient) -> None:
    resp = await client.get("/admin/login")
    assert resp.status_code == 200
    assert "Sign In" in resp.text


@pytest.mark.asyncio
async def test_valid_login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/" in resp.headers["location"]


@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 200
    assert "Invalid" in resp.text


@pytest.mark.asyncio
async def test_nonadmin_user_denied(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/login",
        data={"username": "nonadmin", "password": "nonadmin"},
    )
    assert resp.status_code == 200
    assert "Invalid" in resp.text


@pytest.mark.asyncio
async def test_logout(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/logout", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login" in resp.headers["location"]

    # After logout, accessing dashboard should redirect to login
    resp = await authed_client.get("/admin/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login" in resp.headers["location"]
