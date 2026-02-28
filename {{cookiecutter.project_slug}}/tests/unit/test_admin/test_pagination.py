"""Unit tests for pagination math (US2)."""

import math


def compute_pagination(page: int, page_size: int, total_count: int) -> dict:
    """Compute pagination values — mirrors admin list view logic."""
    total_pages = max(1, math.ceil(total_count / page_size)) if page_size > 0 else 1
    offset = (page - 1) * page_size
    has_prev = page > 1
    has_next = page < total_pages
    return {
        "offset": offset,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
    }


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
