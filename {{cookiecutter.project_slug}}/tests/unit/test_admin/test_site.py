"""Unit tests for AdminSite (US1)."""

import pytest

from app.admin.resource import ColumnConfig, FieldConfig, FieldType, ResourceAdmin
from app.admin.site import AdminSite


class _StubDAO:
    async def list(self, offset, limit, search=None):
        return [], 0

    async def get(self, id):
        return None

    async def create(self, data):
        return data

    async def update(self, id, data):
        return data

    async def delete(self, id):
        pass


def _make_resource(name: str = "items") -> ResourceAdmin:
    return ResourceAdmin(
        name=name,
        display_name=name.title(),
        dao=_StubDAO(),
        list_columns=[ColumnConfig(name="id", label="ID")],
        form_fields=[FieldConfig(name="name", label="Name", field_type=FieldType.TEXT)],
    )


def test_register_accepts_valid_resource() -> None:
    site = AdminSite()
    res = _make_resource()
    site.register(res)
    assert site.get_resources() == [res]


def test_register_duplicate_raises() -> None:
    site = AdminSite()
    site.register(_make_resource("items"))
    with pytest.raises(ValueError, match="already registered"):
        site.register(_make_resource("items"))


def test_get_resources_returns_registration_order() -> None:
    site = AdminSite()
    r1 = _make_resource("alpha")
    r2 = _make_resource("beta")
    site.register(r1)
    site.register(r2)
    assert site.get_resources() == [r1, r2]


def test_get_router_fails_if_no_resources() -> None:
    site = AdminSite()
    with pytest.raises(RuntimeError, match="No resources registered"):
        site.get_router()
