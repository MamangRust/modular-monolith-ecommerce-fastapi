"""Email consumer handler. Per-message flow, matching the `ConsumeClaim` body: 1. unmarshal + validate the envelope — invalid messages are committed as poison (never reach SMTP); 2. dedup through the Postgres consumer inbox keyed on `"<topic>:<event_id>"` (the envelope's event id, NOT the Kafka key: two distinct events for the same entity must both be delivered); 3. send via SMTP; a transient failure **releases** the inbox lease and offloads the payload to the retry topic with attempt-1 headers; 4. success marks the inbox row processed; 5. the offset is committed only after a terminal outcome (poison, dedup hit, retry offload, or success) — an inbox/producer error raises, leaving the offset uncommitted for redelivery (`return err`)."""

from __future__ import annotations

from typing import Any, Protocol

from pkg.emailretry import (
    RETRY_TOPIC,
    RetryMeta,
    build_headers,
    next_retry_at,
)
from pkg.event import EmailEnvelope
from pkg.logger.logger import Logger
from service.email import metrics

CONSUMER_GROUP = "email-service-group"


class RetryPublisher(Protocol):
    async def send_message_with_headers(
        self,
        topic: str,
        key: str,
        value: bytes | str,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None: ...


class MailerLike(Protocol):
    async def send(self, to: str, subject: str, body: str) -> None: ...


class InboxLike(Protocol):
    """ConsumerInbox` interface."""

    async def reserve(
        self,
        consumer_name: str,
        event_key: str,
        topic: str,
        partition: int,
        offset: int,
    ) -> Any: ...

    async def mark_processed(
        self, consumer_name: str, event_key: str, reservation_version: int
    ) -> None: ...

    async def release(
        self,
        consumer_name: str,
        event_key: str,
        reservation_version: int,
        processing_error: str | None = None,
    ) -> None: ...


class EmailHandler:
    def __init__(
        self,
        logger: Logger,
        mailer: MailerLike,
        inbox: InboxLike | None,
        consumer_name: str,
        producer: RetryPublisher | None,
        retry_backoff_seconds: float,
    ) -> None:
        self._logger = logger
        self._mailer = mailer
        self._inbox = inbox
        self._consumer_name = consumer_name
        self._producer = producer
        self._retry_backoff = retry_backoff_seconds

    async def handle(self, msg: Any, commit: Any) -> None:
        try:
            payload = EmailEnvelope.from_json(msg.value)
        except (TypeError, ValueError) as exc:
            self._logger.error(
                "Failed to unmarshal message",
                topic=getattr(msg, "topic", ""),
                error=str(exc),
            )
            metrics.record(metrics.EMAIL_INVALID)
            await commit(msg)
            return

        if not payload.is_valid():
            self._logger.error(
                "Invalid email envelope: event_id, schema_version=1, event_type, "
                "email, subject and body are required"
            )
            metrics.record(metrics.EMAIL_INVALID)
            await commit(msg)
            return

        event_key = f"{msg.topic}:{payload.event_id}"
        reservation_version = 0
        if self._inbox is not None:
            try:
                reservation = await self._inbox.reserve(
                    self._consumer_name,
                    event_key,
                    msg.topic,
                    msg.partition,
                    msg.offset,
                )
            except Exception:
                raise
            if reservation.processed:
                # The side effect was already completed by this consumer.
                await commit(msg)
                return
            if not reservation.reserved:
                raise RuntimeError(
                    f"consumer inbox lease is active for event {event_key}"
                )
            reservation_version = reservation.reservation_version

        try:
            await self._mailer.send(payload.email, payload.subject, payload.body)
        except Exception as exc:
            self._logger.error(
                "Failed to send email; offloading to retry topic", error=str(exc)
            )
            if self._inbox is not None:
                try:
                    await self._inbox.release(
                        self._consumer_name, event_key, reservation_version, str(exc)
                    )
                except Exception as release_exc:
                    self._logger.error(
                        "failed to release consumer inbox lease",
                        event_key=event_key,
                        error=str(release_exc),
                    )
            metrics.record(metrics.EMAIL_FAILED)

            if self._producer is None:
                raise
            meta = RetryMeta(
                src_topic=msg.topic,
                src_partition=msg.partition,
                src_offset=msg.offset,
                attempt=1,
                retry_at=next_retry_at(1, self._retry_backoff),
                reason=str(exc),
            )
            try:
                await self._producer.send_message_with_headers(
                    RETRY_TOPIC, payload.event_id, msg.value, build_headers(meta)
                )
            except Exception as pub_exc:
                raise RuntimeError(f"publish to retry topic: {pub_exc}") from pub_exc
            metrics.record(metrics.EMAIL_RETRIED)
            await commit(msg)
            return

        metrics.record(metrics.EMAIL_SENT)
        if self._inbox is not None:
            await self._inbox.mark_processed(
                self._consumer_name, event_key, reservation_version
            )
        await commit(msg)


__all__ = ["CONSUMER_GROUP", "EmailHandler", "RetryPublisher"]
