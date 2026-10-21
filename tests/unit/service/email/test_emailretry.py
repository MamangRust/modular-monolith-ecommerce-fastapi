"""Unit tests for the email retry/DLQ contract.

Headers round-trip, the linear backoff + 10-minute cap, DLQ attempt counting,
and the poison-meta parse errors."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pkg.emailretry import (
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


def test_topic_constants() -> None:
    assert RETRY_TOPIC == "email-service-topic-email-retry"
    assert DLQ_TOPIC == "email-service-topic-email-dlq"
    assert RETRY_GROUP == "email-service-retry-group"
    assert DEFAULT_MAX_ATTEMPTS == 5
    assert DEFAULT_BACKOFF_SECONDS == 30.0


def test_headers_round_trip() -> None:
    meta = RetryMeta(
        src_topic="email-service-topic-transaction-create",
        src_partition=2,
        src_offset=41,
        attempt=3,
        retry_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        reason="smtp down",
    )
    parsed = parse_meta(build_headers(meta))
    assert parsed == meta


def test_dlq_headers_carry_final_attempts() -> None:
    meta = RetryMeta(
        src_topic="t",
        src_partition=0,
        src_offset=1,
        attempt=5,
        retry_at=datetime.now(UTC),
        reason="boom",
        attempts=5,
    )
    headers = {k.decode(): v for k, v in build_dlq_headers(meta)}
    assert headers["_attempts"] == b"5"
    parsed = parse_meta(build_dlq_headers(meta))
    assert parsed.attempts == 5
    assert parsed.attempt == 5


def test_parse_meta_missing_headers_is_poison() -> None:
    with pytest.raises(MissingRetryMetaError):
        parse_meta(None)
    with pytest.raises(MissingRetryMetaError):
        parse_meta([])
    with pytest.raises(MissingRetryMetaError):
        parse_meta([(b"_attempt", b"1")])


def test_parse_meta_invalid_fields_is_poison() -> None:
    good = build_headers(
        RetryMeta(
            src_topic="t",
            src_partition=0,
            src_offset=0,
            attempt=1,
            retry_at=datetime.now(UTC),
        )
    )
    corrupt = {k.decode(): v for k, v in good}
    corrupt["_srcPartition"] = b"abc"
    with pytest.raises(MissingRetryMetaError):
        parse_meta([(k.encode(), v) for k, v in corrupt.items()])
    corrupt2 = {k.decode(): v for k, v in good}
    corrupt2["_retryAt"] = b"not-a-date"
    with pytest.raises(MissingRetryMetaError):
        parse_meta([(k.encode(), v) for k, v in corrupt2.items()])


def test_backoff_is_linear_and_capped() -> None:
    assert backoff(1) == 30.0
    assert backoff(2) == 60.0
    assert backoff(3, 5.0) == 15.0
    assert backoff(0) == 30.0  # clamped to attempt 1
    assert backoff(100) == MAX_BACKOFF_SECONDS  # capped at 10 minutes
    assert backoff(1, 0) == 30.0  # non-positive base falls back


def test_next_retry_at_is_future() -> None:
    soon = next_retry_at(1, 30.0)
    assert soon > datetime.now(UTC) - timedelta(seconds=1)
    assert soon <= datetime.now(UTC) + timedelta(seconds=31)
