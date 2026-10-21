"""Kafka retry/DLQ contract for the email service. Retry context rides on the message **headers** (never in the payload) so the payload remains the envelope: replaying a DLQ event only requires republishing the payload to the source topic, and the consumer-side inbox guarantees no duplicate email if the event was already sent. Backoff is **linear** (`base * attempt`), capped at `MAX_BACKOFF` so a retry processor never sleeps for an unbounded period."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_BACKOFF_SECONDS = 30.0
MAX_BACKOFF_SECONDS = 600.0  # 10 minutes

# Shared retry/DLQ topics (emailretry.RetryTopic / DLQTopic / RetryGroup).
RETRY_TOPIC = "email-service-topic-email-retry"
DLQ_TOPIC = "email-service-topic-email-dlq"
RETRY_GROUP = "email-service-retry-group"

# Retry metadata header keys.
HDR_SRC_TOPIC = "_srcTopic"
HDR_SRC_PARTITION = "_srcPartition"
HDR_SRC_OFFSET = "_srcOffset"
HDR_ATTEMPT = "_attempt"
HDR_RETRY_AT = "_retryAt"
HDR_REASON = "_reason"
HDR_ATTEMPTS = "_attempts"


class MissingRetryMetaError(ValueError):
    """A retry-topic message without the required metadata headers (poison)."""


@dataclass
class RetryMeta:
    """Retry/DLQ metadata of one message (emailretry.RetryMeta)."""

    src_topic: str = ""
    src_partition: int = -1
    src_offset: int = -1
    attempt: int = 0
    retry_at: datetime = field(
        default_factory=lambda: datetime(1970, 1, 1, tzinfo=UTC)
    )
    reason: str = ""
    attempts: int = 0  # only set on DLQ messages (final attempt count)


def _fmt_retry_at(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def build_headers(meta: RetryMeta) -> list[tuple[bytes, bytes]]:
    """Serialize meta into aiokafka record headers (Phase 4 contract)."""
    return [
        (HDR_SRC_TOPIC.encode(), meta.src_topic.encode()),
        (HDR_SRC_PARTITION.encode(), str(meta.src_partition).encode()),
        (HDR_SRC_OFFSET.encode(), str(meta.src_offset).encode()),
        (HDR_ATTEMPT.encode(), str(meta.attempt).encode()),
        (HDR_RETRY_AT.encode(), _fmt_retry_at(meta.retry_at).encode()),
        (HDR_REASON.encode(), meta.reason.encode()),
    ]


def build_dlq_headers(meta: RetryMeta) -> list[tuple[bytes, bytes]]:
    """Serialize meta plus the final attempt count into headers."""
    return build_headers(meta) + [
        (HDR_ATTEMPTS.encode(), str(meta.attempts).encode()),
    ]


def parse_meta(headers: list[tuple[bytes, bytes]] | None) -> RetryMeta:
    """Read retry metadata from a consumed message's headers."""
    values: dict[str, str] = {}
    for key, value in headers or []:
        values[key.decode() if isinstance(key, bytes) else key] = (
            value.decode() if isinstance(value, bytes) else value
        )

    meta = RetryMeta(src_topic=values.get(HDR_SRC_TOPIC, ""))
    if not meta.src_topic:
        raise MissingRetryMetaError(
            f"message is missing retry metadata headers: missing {HDR_SRC_TOPIC}"
        )

    try:
        meta.src_partition = int(values.get(HDR_SRC_PARTITION, ""))
    except ValueError as exc:
        raise MissingRetryMetaError(
            f"message is missing retry metadata headers: invalid {HDR_SRC_PARTITION}: {exc}"
        ) from exc

    try:
        meta.src_offset = int(values.get(HDR_SRC_OFFSET, ""))
    except ValueError as exc:
        raise MissingRetryMetaError(
            f"message is missing retry metadata headers: invalid {HDR_SRC_OFFSET}: {exc}"
        ) from exc

    try:
        meta.attempt = int(values.get(HDR_ATTEMPT, ""))
    except ValueError as exc:
        raise MissingRetryMetaError(
            f"message is missing retry metadata headers: invalid {HDR_ATTEMPT}: {exc}"
        ) from exc

    raw_retry_at = values.get(HDR_RETRY_AT, "")
    try:
        meta.retry_at = datetime.fromisoformat(raw_retry_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MissingRetryMetaError(
            f"message is missing retry metadata headers: invalid {HDR_RETRY_AT}: {exc}"
        ) from exc

    meta.reason = values.get(HDR_REASON, "")
    try:
        meta.attempts = int(values.get(HDR_ATTEMPTS, ""))
    except ValueError:
        meta.attempts = 0
    return meta


def backoff(attempt: int, base_seconds: float = DEFAULT_BACKOFF_SECONDS) -> float:
    """Delay before the given attempt: base * attempt, capped at MAX_BACKOFF."""
    if base_seconds <= 0:
        base_seconds = DEFAULT_BACKOFF_SECONDS
    if attempt < 1:
        attempt = 1
    return min(base_seconds * attempt, MAX_BACKOFF_SECONDS)


def next_retry_at(
    attempt: int, base_seconds: float = DEFAULT_BACKOFF_SECONDS
) -> datetime:
    """When the next attempt should run."""
    return datetime.now(UTC) + timedelta(seconds=backoff(attempt, base_seconds))


__all__ = [
    "DEFAULT_BACKOFF_SECONDS",
    "DEFAULT_MAX_ATTEMPTS",
    "DLQ_TOPIC",
    "HDR_ATTEMPT",
    "HDR_ATTEMPTS",
    "HDR_REASON",
    "HDR_RETRY_AT",
    "HDR_SRC_OFFSET",
    "HDR_SRC_PARTITION",
    "HDR_SRC_TOPIC",
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
