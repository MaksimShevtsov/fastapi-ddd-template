"""Shared utilities for the admin panel."""

from __future__ import annotations

import math


def compute_pagination(
    page: int, page_size: int, total_count: int
) -> dict[str, object]:
    """Compute pagination values from page, page_size, and total_count.

    Returns a dict with keys: offset, total_pages, has_prev, has_next.
    """
    total_pages = (
        max(1, math.ceil(total_count / page_size)) if page_size > 0 else 1
    )
    offset = (page - 1) * page_size
    has_prev = page > 1
    has_next = page < total_pages
    return {
        "offset": offset,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
    }
