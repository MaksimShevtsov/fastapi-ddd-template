"""Integration tests for admin list view (US2)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_renders_table(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/")
    assert resp.status_code == 200
    body = resp.text
    assert "Alice" in body
    assert "Bob" in body
    assert "Name" in body  # column header


@pytest.mark.asyncio
async def test_list_pagination(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/?page=1")
    assert resp.status_code == 200
    assert "Page 1" in resp.text


@pytest.mark.asyncio
async def test_list_search(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/?search=alice")
    assert resp.status_code == 200
    assert "Alice" in resp.text
    assert "Bob" not in resp.text


@pytest.mark.asyncio
async def test_list_empty_search(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/users/?search=nonexistent")
    assert resp.status_code == 200
    assert "No records found" in resp.text


@pytest.mark.asyncio
async def test_list_404_unregistered_resource(authed_client: AsyncClient) -> None:
    resp = await authed_client.get("/admin/widgets/")
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()
