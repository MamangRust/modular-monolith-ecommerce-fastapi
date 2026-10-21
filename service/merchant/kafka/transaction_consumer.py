"""Merchant transaction-event consumer. The transaction service publishes `{merchantId}` to `merchant-service-topic-transaction-event`; this consumer evicts the cached merchant so the next read reflects the transaction. runs the group with auto-commit (`StartConsumersWithContext`), so a malformed payload is logged and skipped rather than redelivered; matches that (the `commit` callback is a no-op under auto-commit)."""

from __future__ import annotations

import json
from typing import Any

from pkg.logger.logger import Logger
from service.merchant.redis.interfaces import MerchantCommandCache

TRANSACTION_TOPIC = "merchant-service-topic-transaction-event"
CONSUMER_GROUP = "merchant-service-group"


class MerchantTransactionConsumer:
    def __init__(self, cache: MerchantCommandCache, logger: Logger) -> None:
        self._cache = cache
        self._logger = logger

    async def handle(self, msg: Any, commit: Any) -> None:
        try:
            payload = json.loads(msg.value)
        except (TypeError, ValueError) as exc:
            self._logger.error(
                "invalid transaction event payload",
                topic=getattr(msg, "topic", ""),
                error=str(exc),
            )
            return
        if not isinstance(payload, dict):
            self._logger.error(
                "invalid transaction event payload",
                topic=getattr(msg, "topic", ""),
                error="payload is not a JSON object",
            )
            return

        merchant_id = int(payload.get("merchantId", 0) or 0)
        if self._cache is not None and merchant_id > 0:
            await self._cache.delete_cached_merchant(merchant_id)


__all__ = ["CONSUMER_GROUP", "TRANSACTION_TOPIC", "MerchantTransactionConsumer"]
