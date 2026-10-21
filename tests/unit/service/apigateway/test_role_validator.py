"""Unit tests for the gateway role validator (Kafka faked)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from pkg.logger.logger import Logger
from service.apigateway.middlewares.role_validator import (
    CONSUMER_GROUP,
    REPLY_TOPIC,
    REQUEST_TOPIC,
    RoleValidator,
)
from shared.errors import AppError


class FakeKafka:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str, str]] = []
        self.on_send: Any = None
        self.consumer_args: tuple | None = None

    async def send_message(self, topic: str, key: str, value: str) -> None:
        if self.fail:
            raise RuntimeError("kafka down")
        self.sent.append((topic, key, value))
        if self.on_send is not None:
            await self.on_send(topic, key, value)

    async def start_consumers(self, topics, group_id, handler, manual_commit=False):
        self.consumer_args = (topics, group_id, handler, manual_commit)
        return object()


class FakeCache:
    def __init__(self) -> None:
        self.store: dict[int, list[str]] = {}
        self.sets: list[tuple[int, list[str]]] = []

    async def get_user_roles(self, user_id: int) -> list[str] | None:
        return self.store.get(user_id)

    async def set_user_roles(self, user_id: int, roles: list[str]) -> None:
        self.sets.append((user_id, roles))
        self.store[user_id] = roles


class FakeMsg:
    def __init__(self, value: bytes) -> None:
        self.value = value


def _validator(
    kafka: FakeKafka, cache: FakeCache, timeout: float = 5.0
) -> RoleValidator:
    return RoleValidator(kafka, cache, Logger("test", "error"), timeout=timeout)  # type: ignore[arg-type]


async def test_cache_hit_skips_kafka() -> None:
    kafka, cache = FakeKafka(), FakeCache()
    cache.store[1] = ["Admin_Role_10"]
    validator = _validator(kafka, cache)

    roles = await validator.validate(1)

    assert roles == ["Admin_Role_10"]
    assert kafka.sent == []


async def test_valid_reply_returns_and_caches_roles() -> None:
    kafka, cache = FakeKafka(), FakeCache()
    validator = _validator(kafka, cache)

    async def on_send(topic: str, key: str, value: str) -> None:
        payload = json.loads(value)
        await validator._handle_response(
            FakeMsg(
                json.dumps(
                    {
                        "correlation_id": payload["correlation_id"],
                        "valid": True,
                        "role_names": ["Admin_Role_10"],
                    }
                ).encode()
            ),
            None,
        )

    kafka.on_send = on_send
    roles = await validator.validate(7)

    assert roles == ["Admin_Role_10"]
    assert cache.sets == [(7, ["Admin_Role_10"])]
    topic, key, raw = kafka.sent[0]
    assert topic == REQUEST_TOPIC
    assert json.loads(raw)["reply_topic"] == REPLY_TOPIC


async def test_invalid_reply_raises_401() -> None:
    kafka, cache = FakeKafka(), FakeCache()
    validator = _validator(kafka, cache)

    async def on_send(topic: str, key: str, value: str) -> None:
        payload = json.loads(value)
        await validator._handle_response(
            FakeMsg(
                json.dumps(
                    {"correlation_id": payload["correlation_id"], "valid": False, "role_names": []}
                ).encode()
            ),
            None,
        )

    kafka.on_send = on_send
    with pytest.raises(AppError) as excinfo:
        await validator.validate(3)
    assert excinfo.value.code == 401
    assert validator.pending_count == 0


async def test_timeout_raises_408() -> None:
    kafka, cache = FakeKafka(), FakeCache()
    validator = _validator(kafka, cache, timeout=0.01)

    with pytest.raises(AppError) as excinfo:
        await validator.validate(4)

    assert excinfo.value.code == 408
    assert excinfo.value.message == "Timeout waiting for role validation"
    assert validator.pending_count == 0


async def test_send_failure_raises_500() -> None:
    kafka, cache = FakeKafka(fail=True), FakeCache()
    validator = _validator(kafka, cache)

    with pytest.raises(AppError) as excinfo:
        await validator.validate(5)

    assert excinfo.value.code == 500
    assert validator.pending_count == 0


async def test_start_registers_consumer_with_expected_group() -> None:
    kafka, cache = FakeKafka(), FakeCache()
    validator = _validator(kafka, cache)
    await validator.start()
    assert kafka.consumer_args is not None
    topics, group_id, handler, manual = kafka.consumer_args
    assert topics == [REPLY_TOPIC]
    assert group_id == CONSUMER_GROUP
    assert manual is False


async def test_close_cancels_pending() -> None:
    kafka, cache = FakeKafka(), FakeCache()
    validator = _validator(kafka, cache, timeout=5.0)
    task = asyncio.create_task(validator.validate(9))
    await asyncio.sleep(0)
    await validator.close()
    with pytest.raises((AppError, asyncio.CancelledError)):
        await task
