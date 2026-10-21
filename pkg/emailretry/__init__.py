"""Kafka retry/DLQ contract for the email service."""

from pkg.emailretry.retry import (
    DEFAULT_BACKOFF_SECONDS,
    DEFAULT_MAX_ATTEMPTS,
    DLQ_TOPIC,
    MAX_BACKOFF_SECONDS,
    RETRY_GROUP,
    RETRY_TOPIC,
    MissingRetryMetaError,
    RetryMeta,
    backoff,
    build_dlq_headers,
    build_headers,
    next_retry_at,
    parse_meta,
)

__all__ = [
    "DEFAULT_BACKOFF_SECONDS",
    "DEFAULT_MAX_ATTEMPTS",
    "DLQ_TOPIC",
    "MAX_BACKOFF_SECONDS",
    "RETRY_GROUP",
    "RETRY_TOPIC",
    "MissingRetryMetaError",
    "RetryMeta",
    "backoff",
    "build_dlq_headers",
    "build_headers",
    "next_retry_at",
    "parse_meta",
]
