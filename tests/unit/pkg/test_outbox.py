"""Unit tests for the transactional outbox (no database required)."""

from __future__ import annotations

import asyncio
import json

import pytest

from pkg.logger.logger import Logger
from pkg.outbox import (
    Event,
    InvalidEventError,
    OutboxRelay,
    RelayConfig,
    enqueue,
)
from pkg.outbox.outbox import _payload_bytes


class FakeResult:
    def __init__(self, rows: list[dict]) -> None:
        self._rows = rows

    def mappings(self) -> FakeResult:
        return self

    def all(self) -> list[dict]:
        return self._rows

    def first(self) -> dict | None:
        return self._rows[0] if self._rows else None


class FakeConn:
    def __init__(self, rows: list[dict] | None = None) -> None:
        self.rows = rows or []
        self.executed: list[tuple[str, dict | None]] = []

    async def execute(self, statement, params=None):
        self.executed.append((str(statement), params))
        return FakeResult(self.rows)


class FakeTransaction:
    def __init__(self, conn: FakeConn) -> None:
        self._conn = conn

    async def __aenter__(self) -> FakeConn:
        return self._conn

    async def __aexit__(self, *exc: object) -> bool:
        return False


class FakeDB:
    def __init__(self, conn: FakeConn) -> None:
        self.conn = conn

    def transaction(self) -> FakeTransaction:
        return FakeTransaction(self.conn)


class FakePublisher:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, str, bytes, int]] = []

    async def send_message_with_retry(
        self, topic: str, key: str, value: bytes, attempts: int
    ) -> None:
        if self.fail:
            raise RuntimeError("kafka down")
        self.calls.append((topic, key, value, attempts))


def _logger() -> Logger:
    return Logger("test", "error")


def test_event_validation_accepts_valid_json() -> None:
    Event("k", "topic", "key", '{"a": 1}').validate()


@pytest.mark.parametrize(
    "event",
    [
        Event("", "topic", "key", "{}"),
        Event("k", "", "key", "{}"),
        Event("k", "topic", "", "{}"),
        Event("k", "topic", "key", "not-json"),
    ],
)
def test_event_validation_rejects_invalid(event: Event) -> None:
    with pytest.raises(InvalidEventError):
        event.validate()


def test_payload_bytes_handles_str_bytes_and_object() -> None:
    assert _payload_bytes("{}") == b"{}"
    assert _payload_bytes(b"{}") == b"{}"
    assert json.loads(_payload_bytes({"a": 1})) == {"a": 1}


async def test_enqueue_uses_on_conflict_do_nothing() -> None:
    conn = FakeConn()
    await enqueue(conn, Event("k1", "topic.one", "key1", '{"a": 1}'))
    statement, params = conn.executed[0]
    assert "ON CONFLICT (event_key) DO NOTHING" in statement
    assert params == {
        "event_key": "k1",
        "topic": "topic.one",
        "message_key": "key1",
        "payload": '{"a": 1}',
    }


async def test_enqueue_rejects_invalid_event_before_touching_db() -> None:
    conn = FakeConn()
    with pytest.raises(InvalidEventError):
        await enqueue(conn, Event("k", "topic", "key", "bad"))
    assert conn.executed == []


def _claimed_row(attempts: int = 1) -> dict:
    return {
        "id": 1,
        "topic": "topic.one",
        "message_key": "key1",
        "payload": '{"a": 1}',
        "attempts": attempts,
        "claim_version": 2,
    }


async def test_run_batch_publishes_and_marks_published() -> None:
    conn = FakeConn([_claimed_row()])
    publisher = FakePublisher()
    relay = OutboxRelay(FakeDB(conn), publisher, _logger())

    processed = await relay.run_batch()

    assert processed == 1
    assert publisher.calls == [("topic.one", "key1", b'{"a": 1}', 1)]
    published = [s for s, _ in conn.executed if "status = 'published'" in s]
    assert len(published) == 1
    assert conn.executed[-1][1] == {"id": 1, "claim_version": 2}

async def test_run_batch_marks_pending_on_publish_failure() -> None:
    conn = FakeConn([_claimed_row(attempts=2)])
    relay = OutboxRelay(FakeDB(conn), FakePublisher(fail=True), _logger(), RelayConfig(max_attempts=10))

    assert await relay.run_batch() == 1

    statement, params = conn.executed[-1]
    assert "CASE WHEN :attempts >= :max_attempts THEN 'failed' ELSE 'pending' END" in statement
    assert params is not None
    assert params["attempts"] == 2
    assert params["backoff_micros"] == 2 * 1_000_000
    assert "kafka down" in params["last_error"]


async def test_run_batch_marks_failed_at_max_attempts() -> None:
    conn = FakeConn([_claimed_row(attempts=3)])
    relay = OutboxRelay(
        FakeDB(conn), FakePublisher(fail=True), _logger(), RelayConfig(max_attempts=3)
    )
    await relay.run_batch()
    _, params = conn.executed[-1]
    assert params is not None
    assert params["attempts"] == 3
    assert params["max_attempts"] == 3


async def test_relay_run_exits_on_stop_event() -> None:
    conn = FakeConn([])
    relay = OutboxRelay(FakeDB(conn), FakePublisher(), _logger(), RelayConfig(poll_interval=0.01))
    stop = asyncio.Event()
    stop.set()
    await asyncio.wait_for(relay.run(stop), timeout=1.0)


def test_relay_requires_db_and_publisher() -> None:
    with pytest.raises(ValueError):
        OutboxRelay(None, FakePublisher(), _logger())
    with pytest.raises(ValueError):
        OutboxRelay(FakeDB(FakeConn()), None, _logger())  # type: ignore[arg-type]
