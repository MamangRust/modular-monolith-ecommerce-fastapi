"""Merchant Kafka consumers."""

from __future__ import annotations

from service.merchant.kafka.transaction_consumer import (
    CONSUMER_GROUP,
    TRANSACTION_TOPIC,
    MerchantTransactionConsumer,
)

__all__ = [
    "CONSUMER_GROUP",
    "TRANSACTION_TOPIC",
    "MerchantTransactionConsumer",
]
