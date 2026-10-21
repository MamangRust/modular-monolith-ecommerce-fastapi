"""Consumer inbox: durable deduplication for Kafka consumers.

Reservations survive consumer restarts/rebalances so at-least-once
redelivery cannot apply the same side effect twice. An expired
processing lease is reclaimed after a crash."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text


class InvalidInboxKeyError(ValueError):
    pass


@dataclass
class InboxReservation:
    reserved: bool
    processed: bool
    reservation_version: int


_RESERVE = """
WITH reserved AS (
    INSERT INTO consumer_inbox (
        consumer_name, event_key, topic, partition_id, message_offset,
        status, attempts, reservation_version, lease_until, last_error, processed_at
    )
    VALUES (:consumer_name, :event_key, :topic, :partition_id, :message_offset,
            'processing', 1, 1,
            current_timestamp + interval '1 minute', '', NULL)
    ON CONFLICT (consumer_name, event_key) DO UPDATE
    SET status = 'processing',
        attempts = consumer_inbox.attempts + 1,
        reservation_version = consumer_inbox.reservation_version + 1,
        lease_until = current_timestamp + interval '1 minute',
        last_error = '',
        topic = EXCLUDED.topic,
        partition_id = EXCLUDED.partition_id,
        message_offset = EXCLUDED.message_offset
    WHERE consumer_inbox.status <> 'processed'
      AND consumer_inbox.lease_until <= current_timestamp
    RETURNING reservation_version
)
SELECT
    EXISTS (SELECT 1 FROM reserved) AS reserved,
    EXISTS (
        SELECT 1
        FROM consumer_inbox ci
        WHERE ci.consumer_name = :consumer_name
          AND ci.event_key = :event_key
          AND ci.status = 'processed'
    ) AS processed,
    COALESCE(
        (SELECT reservation_version FROM reserved),
        (SELECT ci.reservation_version FROM consumer_inbox ci
         WHERE ci.consumer_name = :consumer_name AND ci.event_key = :event_key)
    )::BIGINT AS reservation_version
"""


_MARK_PROCESSED = """
UPDATE consumer_inbox
SET status = 'processed', processed_at = current_timestamp,
    lease_until = current_timestamp, last_error = ''
WHERE consumer_name = :consumer_name AND event_key = :event_key
  AND status = 'processing' AND reservation_version = :reservation_version
"""

_RELEASE = """
UPDATE consumer_inbox
SET status = 'pending', lease_until = current_timestamp,
    last_error = :last_error
WHERE consumer_name = :consumer_name AND event_key = :event_key
  AND status = 'processing' AND reservation_version = :reservation_version
"""


def _check_keys(consumer_name: str, event_key: str) -> None:
    if not consumer_name or not event_key:
        raise InvalidInboxKeyError("invalid consumer inbox key")


class PostgresInbox:
    """Inbox bound to a Database pool. Reservation and completion are
 committed independently: an external side effect cannot share a
 PostgreSQL transaction with the Kafka consumer."""

    def __init__(self, db: Any) -> None:
        if db is None:
            raise ValueError("inbox db is nil")
        self._db = db

    async def reserve(
        self,
        consumer_name: str,
        event_key: str,
        topic: str,
        partition: int,
        offset: int,
    ) -> InboxReservation:
        _check_keys(consumer_name, event_key)
        async with self._db.transaction() as conn:
            result = await conn.execute(
                text(_RESERVE),
                {
                    "consumer_name": consumer_name,
                    "event_key": event_key,
                    "topic": topic,
                    "partition_id": partition,
                    "message_offset": offset,
                },
            )
            row = result.mappings().first()
        if row is None:
            raise RuntimeError("inbox reserve returned no row")
        return InboxReservation(
            reserved=bool(row["reserved"]),
            processed=bool(row["processed"]),
            reservation_version=int(row["reservation_version"]),
        )

    async def mark_processed(self, consumer_name: str, event_key: str, reservation_version: int) -> None:
        _check_keys(consumer_name, event_key)
        async with self._db.transaction() as conn:
            await conn.execute(
                text(_MARK_PROCESSED),
                {
                    "consumer_name": consumer_name,
                    "event_key": event_key,
                    "reservation_version": reservation_version,
                },
            )

    async def release(
        self,
        consumer_name: str,
        event_key: str,
        reservation_version: int,
        processing_error: str | None = None,
    ) -> None:
        _check_keys(consumer_name, event_key)
        last_error = processing_error or "consumer processing failed"
        async with self._db.transaction() as conn:
            await conn.execute(
                text(_RELEASE),
                {
                    "consumer_name": consumer_name,
                    "event_key": event_key,
                    "reservation_version": reservation_version,
                    "last_error": last_error,
                },
            )
