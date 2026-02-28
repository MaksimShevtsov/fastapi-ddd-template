"""Unit tests for ResourceAdmin validation (US4)."""

import pytest

from app.admin.resource import ColumnConfig, FieldConfig, FieldType, ResourceAdmin


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


def _dao() -> _StubDAO:
    return _StubDAO()


def test_valid_resource_creation() -> None:
    r = ResourceAdmin(
        name="users",
        display_name="Users",
        dao=_dao(),
        list_columns=[ColumnConfig(name="id", label="ID")],
        form_fields=[FieldConfig(name="name", label="Name", field_type=FieldType.TEXT)],
    )
    assert r.name == "users"


def test_name_must_be_valid_slug() -> None:
    with pytest.raises(ValueError, match="lowercase alphanumeric"):
        ResourceAdmin(
            name="Invalid Name",
            display_name="Invalid",
            dao=_dao(),
            list_columns=[ColumnConfig(name="id", label="ID")],
            form_fields=[
                FieldConfig(name="name", label="Name", field_type=FieldType.TEXT)
            ],
        )


def test_name_with_hyphens_is_valid() -> None:
    r = ResourceAdmin(
        name="order-items",
        display_name="Order Items",
        dao=_dao(),
        list_columns=[ColumnConfig(name="id", label="ID")],
        form_fields=[FieldConfig(name="name", label="Name", field_type=FieldType.TEXT)],
    )
    assert r.name == "order-items"


def test_empty_list_columns_raises() -> None:
    with pytest.raises(ValueError, match="list_columns must not be empty"):
        ResourceAdmin(
            name="items",
            display_name="Items",
            dao=_dao(),
            list_columns=[],
            form_fields=[
                FieldConfig(name="name", label="Name", field_type=FieldType.TEXT)
            ],
        )


def test_empty_form_fields_raises() -> None:
    with pytest.raises(ValueError, match="form_fields must not be empty"):
        ResourceAdmin(
            name="items",
            display_name="Items",
            dao=_dao(),
            list_columns=[ColumnConfig(name="id", label="ID")],
            form_fields=[],
        )


def test_id_field_must_exist() -> None:
    with pytest.raises(ValueError, match="id_field"):
        ResourceAdmin(
            name="items",
            display_name="Items",
            dao=_dao(),
            list_columns=[ColumnConfig(name="name", label="Name")],
            form_fields=[
                FieldConfig(name="name", label="Name", field_type=FieldType.TEXT)
            ],
            id_field="nonexistent",
        )


def test_select_field_requires_choices() -> None:
    with pytest.raises(ValueError, match="choices"):
        ResourceAdmin(
            name="items",
            display_name="Items",
            dao=_dao(),
            list_columns=[ColumnConfig(name="id", label="ID")],
            form_fields=[
                FieldConfig(name="status", label="Status", field_type=FieldType.SELECT)
            ],
        )


def test_all_field_types() -> None:
    r = ResourceAdmin(
        name="items",
        display_name="Items",
        dao=_dao(),
        list_columns=[ColumnConfig(name="id", label="ID")],
        form_fields=[
            FieldConfig(name="title", label="Title", field_type=FieldType.TEXT),
            FieldConfig(name="count", label="Count", field_type=FieldType.NUMBER),
            FieldConfig(name="active", label="Active", field_type=FieldType.BOOLEAN),
            FieldConfig(name="date", label="Date", field_type=FieldType.DATE),
            FieldConfig(
                name="timestamp", label="Timestamp", field_type=FieldType.DATETIME
            ),
            FieldConfig(
                name="status",
                label="Status",
                field_type=FieldType.SELECT,
                choices=[("a", "Active"), ("i", "Inactive")],
            ),
            FieldConfig(
                name="desc", label="Description", field_type=FieldType.TEXTAREA
            ),
        ],
    )
    assert len(r.form_fields) == 7


def test_column_config_link_to_detail() -> None:
    col = ColumnConfig(name="name", label="Name", link_to_detail=True)
    assert col.link_to_detail is True
