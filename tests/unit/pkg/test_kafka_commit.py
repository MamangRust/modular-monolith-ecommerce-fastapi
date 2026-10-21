"""Unit tests for the managed Kafka consumer's manual-commit path.

Regression cover for a bug found by running the card service against a real
broker: `_make_commit` forwarded the `ConsumerRecord` straight to
`aiokafka.AIOKafkaConsumer.commit()`, which expects a
`{TopicPartition: next_offset}` mapping. aiokafka's `commit_structure_validate`
rejects it with `ValueError(record)`, so `str(exc)` printed the whole record and
— more importantly — a manual-commit consumer could never advance its offset.
Every message failed, was redelivered, and the consume loop restarted forever.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from types import SimpleNamespace
from typing import Any

from aiokafka.structs import TopicPartition

from pkg.kafka.kafka import AsyncManagedConsumer
from pkg.logger.logger import get_logger


class FakeConsumer:
    """Captures what the commit callback hands to `commit()`."""

    def __init__(self) -> None:
        self.committed: list[Any] = []

    async def commit(self, offsets: Any = None) -> None:
        self.committed.append(offsets)


async def _noop(msg: Any, commit: Callable[[Any], Awaitable[None]]) -> None:
    return None


def _consumer(manual: bool = True) -> AsyncManagedConsumer:
    return AsyncManagedConsumer(
        logger=get_logger("test-kafka"),
        brokers=["localhost:9092"],
        topics=["card.limit.changed"],
        group_id="card-event-log-group",
        handler=_noop,
        manual_commit=manual,
    )


def _msg(offset: int = 41) -> SimpleNamespace:
    return SimpleNamespace(
        topic="card.limit.changed",
        partition=2,
        offset=offset,
        key=b"4862277462775055",
        value=b'{"card_number": "4862277462775055"}',
    )


async def test_manual_commit_sends_next_offset_mapping() -> None:
    managed = _consumer()
    fake = FakeConsumer()
    commit = managed._make_commit(fake, _msg())

    await commit(_msg())

    assert fake.committed == [{TopicPartition("card.limit.changed", 2): 42}]


async def test_manual_commit_commits_offset_plus_one() -> None:
    managed = _consumer()
    fake = FakeConsumer()
    commit = managed._make_commit(fake, _msg())

    await commit(_msg(offset=0))

    assert fake.committed[0][TopicPartition("card.limit.changed", 2)] == 1


async def test_auto_commit_mode_never_calls_commit() -> None:
    managed = _consumer(manual=False)
    fake = FakeConsumer()
    commit = managed._make_commit(fake, _msg())

    await commit(_msg())

    assert fake.committed == []


__all__ = [
    "test_auto_commit_mode_never_calls_commit",
    "test_manual_commit_commits_offset_plus_one",
    "test_manual_commit_sends_next_offset_mapping",
]
