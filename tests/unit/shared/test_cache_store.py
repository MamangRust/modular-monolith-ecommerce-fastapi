"""Unit tests for CacheStore and convert helpers (no Redis required)."""

from __future__ import annotations

import fnmatch
from datetime import datetime
from typing import Any

from pkg.logger.logger import Logger
from shared.cache import CacheStore
from shared.convert import (
    format_time_ptr,
    format_time_rfc3339,
    int32_val,
    str_val,
    time_to_wrappers,
)


class FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.fail = False

    def _guard(self) -> None:
        if self.fail:
            raise RuntimeError("redis down")

    async def get(self, key: str) -> str | None:
        self._guard()
        return self.data.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self._guard()
        self.data[key] = value
        return True

    async def delete(self, *keys: str) -> int:
        self._guard()
        removed = 0
        for key in keys:
            if key in self.data:
                removed += 1
                del self.data[key]
        return removed

    async def scan_iter(self, match: str | None = None, count: int | None = None):
        self._guard()
        for key in list(self.data):
            if match is None or fnmatch.fnmatch(key, match):
                yield key

    async def dbsize(self) -> int:
        self._guard()
        return len(self.data)

    async def info(self, section: str | None = None) -> dict[str, Any]:
        self._guard()
        return {"used_memory": 1024, "used_memory_human": "1K"}


def _store(fake: FakeRedis | None = None) -> tuple[CacheStore, FakeRedis]:
    redis = fake or FakeRedis()
    return CacheStore(redis, Logger("test", "error")), redis


async def test_set_get_delete_roundtrip() -> None:
    store, _ = _store()
    assert await store.set("k", "v", 60) is True
    assert await store.get("k") == "v"
    assert await store.delete("k") == 1
    assert await store.get("k") is None


async def test_json_roundtrip() -> None:
    store, _ = _store()
    await store.set_json("j", {"a": [1, 2], "b": "x"}, 60)
    assert await store.get_json("j") == {"a": [1, 2], "b": "x"}


async def test_get_json_invalid_payload_returns_none() -> None:
    store, redis = _store()
    redis.data["bad"] = "not-json"
    assert await store.get_json("bad") is None


async def test_invalidate_uses_scan_pattern() -> None:
    store, _ = _store()
    await store.set("role:id:1", "a", 60)
    await store.set("role:id:2", "b", 60)
    await store.set("role:all:page:1:pageSize:10:search:", "c", 60)
    assert await store.invalidate("role:id:*") == 2
    assert await store.get("role:id:1") is None
    assert await store.get("role:all:page:1:pageSize:10:search:") == "c"


async def test_cache_outage_does_not_raise() -> None:
    store, redis = _store()
    redis.fail = True
    assert await store.get("k") is None
    assert await store.set("k", "v", 60) is False
    assert await store.delete("k") == 0
    assert await store.invalidate("k:*") == 0
    assert (await store.stats())["total_keys"] == 0


async def test_prefix_applied() -> None:
    store, redis = _store()
    store = CacheStore(redis, Logger("test", "error"), prefix="svc:")
    await store.set("k", "v", 60)
    assert "svc:k" in redis.data


def test_convert_helpers() -> None:
    moment = datetime(2026, 1, 2, 3, 4, 5)
    assert format_time_ptr(moment) == "2026-01-02 03:04:05"
    assert format_time_ptr(None) == ""
    # Naive datetimes are treated as UTC (time.Time has no tz question).
    assert format_time_rfc3339(moment) == "2026-01-02T03:04:05Z"
    assert format_time_rfc3339(None) == ""
    assert str_val(None) == ""
    assert int32_val(None) == 0
    assert time_to_wrappers(None) is None
    wrapper = time_to_wrappers(moment)
    assert wrapper is not None and wrapper.value == "2026-01-02T03:04:05Z"
