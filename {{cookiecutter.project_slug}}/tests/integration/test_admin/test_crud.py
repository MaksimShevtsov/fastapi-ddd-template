"""Integration tests for admin CRUD operations (US3)."""

import re

import pytest
from httpx import AsyncClient


def _extract_csrf(html: str) -> str:
    """Extract CSRF token from hidden input in rendered HTML."""
    match = re.search(r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"', html)
    assert match, "CSRF token not found in HTML"
    return match.group(1)


@pytest.mark.asyncio
async def test_create_form_renders(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/create")
    assert resp.status_code == 200
    assert "Name" in resp.text
    assert "Email" in resp.text
    assert "Role" in resp.text


@pytest.mark.asyncio
async def test_create_valid_record(authed_client: AsyncClient) -> None:
    form_resp = await authed_client.get("/admin/users/create")
    csrf = _extract_csrf(form_resp.text)
    resp = await authed_client.post(
        "/admin/users/create",
        data={
            "name": "NewUser",
            "email": "new@example.com",
            "role": "user",
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/users/" in resp.headers["location"]


@pytest.mark.asyncio
async def test_create_invalid_required_field(authed_client: AsyncClient) -> None:
    form_resp = await authed_client.get("/admin/users/create")
    csrf = _extract_csrf(form_resp.text)
    resp = await authed_client.post(
        "/admin/users/create",
        data={"name": "", "email": "new@example.com", "role": "user", "csrf_token": csrf},
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
    form_resp = await authed_client.get("/admin/users/1/edit")
    csrf = _extract_csrf(form_resp.text)
    resp = await authed_client.post(
        "/admin/users/1/edit",
        data={
            "name": "Alice Updated",
            "email": "alice@example.com",
            "role": "admin",
            "csrf_token": csrf,
        },
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
    confirm_resp = await authed_client.get("/admin/users/1/delete")
    csrf = _extract_csrf(confirm_resp.text)
    resp = await authed_client.post(
        "/admin/users/1/delete",
        data={"csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/users/" in resp.headers["location"]


@pytest.mark.asyncio
async def test_delete_nonexistent_shows_error(authed_client: AsyncClient) -> None:
    confirm_resp = await authed_client.get("/admin/users/1/delete")
    csrf = _extract_csrf(confirm_resp.text)
    resp = await authed_client.post(
        "/admin/users/nonexistent/delete",
        data={"csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 303
