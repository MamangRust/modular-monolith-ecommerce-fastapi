"""Transactional outbox.

An event is inserted in the *same* transaction as the business mutation
(`enqueue`), then published to Kafka asynchronously by `OutboxRelay`.
Delivery is at-least-once; consumers deduplicate through `PostgresInbox`.

Claiming uses `FOR UPDATE SKIP LOCKED` so several relay replicas can run
without double-publishing, and every state transition is fenced by
`claim_version` so a relay that stalled past its lease cannot clobber a
row another relay has already reclaimed."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from sqlalchemy import text

from pkg.logger.logger import Logger

_ENQUEUE = """
INSERT INTO outbox_events (event_key, topic, message_key, payload)
VALUES (:event_key, :topic, :message_key, CAST(:payload AS jsonb))
ON CONFLICT (event_key) DO NOTHING
"""

_CLAIM = """
WITH candidates AS (
    SELECT id FROM outbox_events
    WHERE ((status = 'pending' AND next_attempt_at <= current_timestamp)
        OR (status = 'publishing' AND updated_at < current_timestamp - interval '1 minute'))
    ORDER BY id
    FOR UPDATE SKIP LOCKED
    LIMIT :batch_size
)
UPDATE outbox_events e
SET status = 'publishing',
    attempts = e.attempts + 1,
    claim_version = e.claim_version + 1,
    updated_at = current_timestamp
FROM candidates c
WHERE e.id = c.id
RETURNING e.id, e.topic, e.message_key, e.payload, e.attempts, e.claim_version
"""

_CLAIM_BY_TOPICS = """
WITH candidates AS (
    SELECT id FROM outbox_events
    WHERE topic = ANY(:topics)
      AND ((status = 'pending' AND next_attempt_at <= current_timestamp)
        OR (status = 'publishing' AND updated_at < current_timestamp - interval '1 minute'))
    ORDER BY id
    FOR UPDATE SKIP LOCKED
    LIMIT :batch_size
)
UPDATE outbox_events e
SET status = 'publishing',
    attempts = e.attempts + 1,
    claim_version = e.claim_version + 1,
    updated_at = current_timestamp
FROM candidates c
WHERE e.id = c.id
RETURNING e.id, e.topic, e.message_key, e.payload, e.attempts, e.claim_version
"""

_MARK_PUBLISHED = """
UPDATE outbox_events
SET status = 'published',
    published_at = current_timestamp,
    updated_at = current_timestamp,
    last_error = ''
WHERE id = :id AND status = 'publishing' AND claim_version = :claim_version
"""

_MARK_FAILED = """
UPDATE outbox_events
SET status = CASE WHEN :attempts >= :max_attempts THEN 'failed' ELSE 'pending' END,
    next_attempt_at = CASE
        WHEN :attempts >= :max_attempts THEN next_attempt_at
        ELSE current_timestamp + (:backoff_micros * interval '1 microsecond')
    END,
    updated_at = current_timestamp,
    last_error = :last_error
WHERE id = :id AND status = 'publishing' AND claim_version = :claim_version
"""


class InvalidEventError(ValueError):
    """An outbox event is missing required fields or has a non-JSON payload."""


@dataclass
class Event:
    event_key: str
    topic: str
    key: str
    payload: bytes | str

    def validate(self) -> None:
        if not self.event_key or not self.topic or not self.key:
            raise InvalidEventError("outbox event key, topic and message key are required")
        try:
            json.loads(self.payload)
        except (TypeError, ValueError) as exc:
            raise InvalidEventError("outbox event payload must be valid JSON") from exc


@dataclass
class ClaimedEvent:
    id: int
    topic: str
    key: str
    payload: bytes
    attempts: int
    claim_version: int


def _payload_text(payload: bytes | str) -> str:
    if isinstance(payload, (bytes, bytearray)):
        return bytes(payload).decode("utf-8")
    return payload


def _payload_bytes(payload: Any) -> bytes:
    """Normalise a JSONB column back to wire bytes.

asyncpg may hand back JSONB as str (default) or a decoded object
 depending on the codec; handle both so relay behaviour is stable."""
    if isinstance(payload, (bytes, bytearray)):
        return bytes(payload)
    if isinstance(payload, str):
        return payload.encode("utf-8")
    return json.dumps(payload).encode("utf-8")


async def enqueue(conn: Any, event: Event) -> None:
    """Insert the event inside the caller's transaction.

`conn` must be the AsyncConnection from `Database.transaction` so
 the outbox row commits atomically with the business mutation."""
    event.validate()
    await conn.execute(
        text(_ENQUEUE),
        {
            "event_key": event.event_key,
            "topic": event.topic,
            "message_key": event.key,
            "payload": _payload_text(event.payload),
        },
    )


@runtime_checkable
class Publisher(Protocol):
    async def send_message_with_retry(
        self, topic: str, key: str, value: bytes, attempts: int
    ) -> None: ...


@dataclass
class RelayConfig:
    batch_size: int = 50
    poll_interval: float = 1.0
    max_attempts: int = 10
    base_backoff: float = 1.0
    topics: list[str] = field(default_factory=list)


class OutboxRelay:
    """Polls the outbox and publishes pending events to Kafka."""

    def __init__(
        self,
        db: Any,
        publisher: Publisher,
        logger: Logger,
        config: RelayConfig | None = None,
    ) -> None:
        if db is None:
            raise ValueError("outbox relay db is nil")
        if publisher is None:
            raise ValueError("outbox relay publisher is nil")
        self._db = db
        self._publisher = publisher
        self._logger = logger
        self._config = config or RelayConfig()

    @property
    def config(self) -> RelayConfig:
        return self._config

    async def run(self, stop_event: asyncio.Event) -> None:
        self._logger.info("outbox relay started", batch_size=self._config.batch_size)
        while not stop_event.is_set():
            processed = 0
            try:
                processed = await self.run_batch()
            except Exception as exc:  # transient DB/Kafka failures keep the relay alive
                self._logger.error("outbox relay batch failed", error=str(exc))
            if processed == 0:
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=self._config.poll_interval)
                except TimeoutError:
                    pass
        self._logger.info("outbox relay stopped")

    async def run_batch(self) -> int:
        events = await self._claim()
        for event in events:
            await self._publish(event)
        return len(events)

    async def _claim(self) -> list[ClaimedEvent]:
        cfg = self._config
        if cfg.topics:
            sql, params = _CLAIM_BY_TOPICS, {
                "batch_size": cfg.batch_size,
                "topics": list(cfg.topics),
            }
        else:
            sql, params = _CLAIM, {"batch_size": cfg.batch_size}
        async with self._db.transaction() as conn:
            result = await conn.execute(text(sql), params)
            rows = result.mappings().all()
        return [
            ClaimedEvent(
                id=int(row["id"]),
                topic=row["topic"],
                key=row["message_key"] or "",
                payload=_payload_bytes(row["payload"]),
                attempts=int(row["attempts"]),
                claim_version=int(row["claim_version"]),
            )
            for row in rows
        ]

    async def _publish(self, event: ClaimedEvent) -> None:
        try:
            await self._publisher.send_message_with_retry(event.topic, event.key, event.payload, 1)
        except Exception as exc:
            await self._mark_failed(event, str(exc))
            self._logger.error(
                "outbox event publish failed",
                outbox_id=event.id,
                topic=event.topic,
                attempts=event.attempts,
                error=str(exc),
            )
            return
        await self._mark_published(event)
        self._logger.debug("outbox event published", outbox_id=event.id, topic=event.topic)

    async def _mark_published(self, event: ClaimedEvent) -> None:
        async with self._db.transaction() as conn:
            await conn.execute(
                text(_MARK_PUBLISHED),
                {"id": event.id, "claim_version": event.claim_version},
            )

    async def _mark_failed(self, event: ClaimedEvent, last_error: str) -> None:
        cfg = self._config
        backoff = cfg.base_backoff * (2 ** (min(event.attempts, 10) - 1))
        async with self._db.transaction() as conn:
            await conn.execute(
                text(_MARK_FAILED),
                {
                    "id": event.id,
                    "claim_version": event.claim_version,
                    "attempts": event.attempts,
                    "max_attempts": cfg.max_attempts,
                    "backoff_micros": int(backoff * 1_000_000),
                    "last_error": last_error[:2000],
                },
            )
