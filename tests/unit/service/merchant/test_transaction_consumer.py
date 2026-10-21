"""Unit tests for the merchant transaction-event consumer.

The transaction service publishes `{merchantId}`; the consumer evicts the
cached merchant. Auto-commit means a malformed payload is logged and skipped
(no redelivery), so the `commit` callback is never required to do anything.
"""

from __future__ import annotations

from typing import Any

from pkg.logger.logger import Logger
from service.merchant.kafka import (
    CONSUMER_GROUP,
    TRANSACTION_TOPIC,
    MerchantTransactionConsumer,
)


class FakeMessage:
    def __init__(self, value: Any, topic: str = TRANSACTION_TOPIC) -> None:
        self.value = value
        self.topic = topic


class FakeCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []

    async def delete_cached_merchant(self, merchant_id: int) -> int:
        self.evicted.append(merchant_id)
        return 1

    async def invalidate_merchant_cache(self) -> int:
        return 1


async def _commit() -> None:
    return None


def _consumer(cache: FakeCache) -> MerchantTransactionConsumer:
    return MerchantTransactionConsumer(cache, Logger("test", "error"))


def test_constants() -> None:
    assert TRANSACTION_TOPIC == "merchant-service-topic-transaction-event"
    assert CONSUMER_GROUP == "merchant-service-group"


async def test_valid_payload_evicts_cache() -> None:
    cache = FakeCache()
    await _consumer(cache).handle(FakeMessage('{"merchantId": 7}'), _commit)
    assert cache.evicted == [7]


async def test_malformed_json_is_skipped() -> None:
    cache = FakeCache()
    await _consumer(cache).handle(FakeMessage("not json"), _commit)
    assert cache.evicted == []


async def test_non_object_payload_is_skipped() -> None:
    cache = FakeCache()
    await _consumer(cache).handle(FakeMessage("[1, 2, 3]"), _commit)
    assert cache.evicted == []


async def test_missing_or_zero_merchant_id_is_skipped() -> None:
    cache = FakeCache()
    await _consumer(cache).handle(FakeMessage("{}"), _commit)
    await _consumer(cache).handle(FakeMessage('{"merchantId": 0}'), _commit)
    assert cache.evicted == []


__all__ = []
