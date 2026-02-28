"""Unit tests for pagination math (US2)."""

from app.admin.utils import compute_pagination


def test_single_page() -> None:
    result = compute_pagination(page=1, page_size=25, total_count=10)
    assert result["total_pages"] == 1
    assert result["offset"] == 0
    assert result["has_prev"] is False
    assert result["has_next"] is False


def test_multiple_pages_first() -> None:
    result = compute_pagination(page=1, page_size=25, total_count=50)
    assert result["total_pages"] == 2
    assert result["has_prev"] is False
    assert result["has_next"] is True


def test_multiple_pages_last() -> None:
    result = compute_pagination(page=2, page_size=25, total_count=50)
    assert result["total_pages"] == 2
    assert result["offset"] == 25
    assert result["has_prev"] is True
    assert result["has_next"] is False


def test_exact_page_boundary() -> None:
    result = compute_pagination(page=1, page_size=25, total_count=25)
    assert result["total_pages"] == 1
    assert result["has_next"] is False


def test_zero_records() -> None:
    result = compute_pagination(page=1, page_size=25, total_count=0)
    assert result["total_pages"] == 1
    assert result["has_prev"] is False
    assert result["has_next"] is False


def test_middle_page() -> None:
    result = compute_pagination(page=3, page_size=10, total_count=50)
    assert result["total_pages"] == 5
    assert result["offset"] == 20
    assert result["has_prev"] is True
    assert result["has_next"] is True
