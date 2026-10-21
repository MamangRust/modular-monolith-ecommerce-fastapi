"""Async database access layer. Keeps the sqlx posture: explicit SQL text executed on a pooled asyncpg connection, no ORM mapping layer. `Database` exposes three primitives: - `select`: read-only, returned connection is rolled back to the pool. - `execute`: write in a dedicated committed transaction (sqlx auto-commit behaviour); returns the first `RETURNING` row. - `execute_all`: like `execute` but returns every `RETURNING` row. Needed because `select` would roll the write back, and `execute` would drop all but the first row. - `transaction`: unit-of-work for multi-statement settlement; financial domains use this so a record mutation, a balance change and an outbox insert share one commit. Pool sizing follows the defaults: max_open=100, min_idle=50, lifetime=1h, idle=30m (via DB_MAX_OPEN_CONNS etc.)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from pkg.config.settings import DatabaseSettings
from pkg.logger.logger import Logger


class Database:
    def __init__(self, engine: AsyncEngine, logger: Logger, settings: DatabaseSettings) -> None:
        self._engine = engine
        self._logger = logger
        self._settings = settings

    @staticmethod
    def create(settings: DatabaseSettings, logger: Logger) -> Database:
        s = settings
        if s.db_min_idle_conns > s.db_max_open_conns:
            min_idle = s.db_max_open_conns
        else:
            min_idle = s.db_min_idle_conns
        url = make_url(s.async_dsn)
        engine = create_async_engine(
            url,
            pool_size=s.db_max_open_conns,
            max_overflow=0,
            pool_timeout=30,
            pool_recycle=s.db_conn_max_lifetime,
            pool_pre_ping=True,
        )
        logger.debug(
            "database engine created",
            pool_size=s.db_max_open_conns,
            min_idle=min_idle,
            lifetime=s.db_conn_max_lifetime,
        )
        return Database(engine, logger, s)

    async def ping(self) -> None:
        async with self._engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        self._logger.info("database connection established")

    async def close(self) -> None:
        await self._engine.dispose()
        self._logger.info("database pool closed")

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as conn:
            yield conn

    async def select(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        async with self._engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return [dict(row) for row in result.mappings().all()]

    async def scalar(self, sql: str, params: dict[str, Any] | None = None) -> Any:
        async with self._engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.mappings().first()

    async def execute(self, sql: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Run a write statement in its own transaction. When the statement has a RETURNING clause, the first row is returned as a dict (sqlx Get semantics); otherwise None."""
        async with self._engine.begin() as conn:
            result = await conn.execute(text(sql), params or {})
            if not result.returns_rows:
                return None
            row = result.mappings().first()
            return dict(row) if row is not None else None

    async def execute_all(
        self, sql: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Run a write statement in its own transaction, returning every row. sqlx `SelectContext` semantics: a data-modifying CTE may legitimately return several rows and must still commit. `select` cannot be used (it rolls back) and `execute` cannot be used (it keeps only the first row)."""
        async with self._engine.begin() as conn:
            result = await conn.execute(text(sql), params or {})
            if not result.returns_rows:
                return []
            return [dict(row) for row in result.mappings().all()]
