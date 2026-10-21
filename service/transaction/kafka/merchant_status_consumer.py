"""Merchant status-event consumer. The merchant service publishes `{merchantId, status}` to `transaction-service-topic-merchant-status-event` when a merchant's status changes; this consumer evicts the whole `transaction:*` cache namespace so the next read reflects the change. runs the group with auto-commit (`StartConsumersWithContext`), so a malformed payload is logged and skipped rather than redelivered; matches that (the `commit` callback is a no-op under auto-commit)."""

from __future__ import annotations

import json
from typing import Any

from pkg.logger.logger import Logger
from service.transaction.redis.interfaces import TransactionCommandCache

MERCHANT_STATUS_TOPIC = "transaction-service-topic-merchant-status-event"
CONSUMER_GROUP = "transaction-service-group"


class MerchantStatusConsumer:
    def __init__(self, cache: TransactionCommandCache, logger: Logger) -> None:
        self._cache = cache
        self._logger = logger

    async def handle(self, msg: Any, commit: Any) -> None:
        try:
            payload = json.loads(msg.value)
        except (TypeError, ValueError) as exc:
            self._logger.error(
                "invalid merchant status event payload",
                topic=getattr(msg, "topic", ""),
                error=str(exc),
            )
            return
        if not isinstance(payload, dict):
            self._logger.error(
                "invalid merchant status event payload",
                topic=getattr(msg, "topic", ""),
                error="payload is not a JSON object",
            )
            return

        _merchant_id = int(payload.get("merchantId", 0) or 0)
        if self._cache is not None:
            await self._cache.invalidate_transaction_cache()


__all__ = ["CONSUMER_GROUP", "MERCHANT_STATUS_TOPIC", "MerchantStatusConsumer"]
