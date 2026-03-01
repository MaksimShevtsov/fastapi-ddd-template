"""Async migration runner for SQLite and PostgreSQL."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from row_query import AsyncEngine

logger = logging.getLogger(__name__)

_MIGRATION_PATTERN = re.compile(r"^(\d+)_(.+)\.sql$")

_CREATE_TRACKING_TABLE: dict[str, str] = {
    "sqlite": (
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version TEXT PRIMARY KEY, "
        "description TEXT NOT NULL, "
        "applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ")"
    ),
    "postgresql": (
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version TEXT PRIMARY KEY, "
        "description TEXT NOT NULL, "
        "applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
        ")"
    ),
}

_INSERT_APPLIED: dict[str, str] = {
    "named": (
        "INSERT INTO schema_migrations (version, description) "
        "VALUES (:version, :description)"
    ),
    "pyformat": (
        "INSERT INTO schema_migrations (version, description) "
        "VALUES (%(version)s, %(description)s)"
    ),
}


async def run_migrations(migration_dir: str | Path, engine: AsyncEngine) -> None:
    """Apply all pending NNN_description.sql migrations in order."""
    migration_dir = Path(migration_dir)
    cm = engine._connection_manager
    driver: str = cm.config.driver
    paramstyle: str = cm.adapter.paramstyle

    create_sql = _CREATE_TRACKING_TABLE.get(driver, _CREATE_TRACKING_TABLE["sqlite"])
    insert_sql = _INSERT_APPLIED.get(paramstyle, _INSERT_APPLIED["named"])

    await cm.initialize_pool()

    async with cm.get_connection() as conn:
        await conn.execute(create_sql)
        await conn.commit()

    async with cm.get_connection() as conn:
        cursor = await conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        rows = await cursor.fetchall()
    applied = {row["version"] for row in rows}

    for migration_file in sorted(migration_dir.glob("*.sql")):
        match = _MIGRATION_PATTERN.match(migration_file.name)
        if not match:
            continue
        version, description = match.group(1), match.group(2)
        if version in applied:
            continue

        logger.info("Applying migration %s_%s", version, description)
        sql = migration_file.read_text(encoding="utf-8")

        async with cm.get_connection() as conn:
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    await conn.execute(stmt)
            await conn.execute(insert_sql, {"version": version, "description": description})
            await conn.commit()

        logger.info("Migration %s applied", version)
