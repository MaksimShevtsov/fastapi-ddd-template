"""Integration tests for admin CRUD operations (US3)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_form_renders(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/create")
    assert resp.status_code == 200
    assert "Name" in resp.text
    assert "Email" in resp.text
    assert "Role" in resp.text


@pytest.mark.asyncio
async def test_create_valid_record(authed_client: AsyncClient) -> None:
    resp = await authed_client.post(
        "/admin/users/create",
        data={"name": "NewUser", "email": "new@example.com", "role": "user"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/users/" in resp.headers["location"]


@pytest.mark.asyncio
async def test_create_invalid_required_field(authed_client: AsyncClient) -> None:
    resp = await authed_client.post(
        "/admin/users/create",
        data={"name": "", "email": "new@example.com", "role": "user"},
    )
    assert resp.status_code == 200
    assert "required" in resp.text.lower()


@pytest.mark.asyncio
async def test_edit_form_prefills(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/1/edit")
    assert resp.status_code == 200
    assert "Alice" in resp.text


@pytest.mark.asyncio
async def test_edit_valid_update(authed_client: AsyncClient) -> None:
    resp = await authed_client.post(
        "/admin/users/1/edit",
        data={"name": "Alice Updated", "email": "alice@example.com", "role": "admin"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/users/1" in resp.headers["location"]


@pytest.mark.asyncio
async def test_delete_confirmation_page(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/1/delete")
    assert resp.status_code == 200
    assert "Confirm Delete" in resp.text


@pytest.mark.asyncio
async def test_delete_removes_record(authed_client: AsyncClient) -> None:
    resp = await authed_client.post(
        "/admin/users/1/delete",
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/users/" in resp.headers["location"]


@pytest.mark.asyncio
async def test_delete_nonexistent_shows_error(authed_client: AsyncClient) -> None:
    resp = await authed_client.post(
        "/admin/users/nonexistent/delete",
        follow_redirects=False,
    )
    assert resp.status_code == 303
