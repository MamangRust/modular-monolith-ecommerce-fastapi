"""Retry/DLQ processor.

Drains the shared retry topic ordered per partition (backoff via the
`_retryAt` header — the handler sleeps until then, capped by
`emailretry.MAX_BACKOFF`), re-attempts SMTP, and escalates:

- success → mark inbox processed + commit;
- transient failure with attempts left → re-publish to the retry topic with
 attempt+1;
- max attempts reached → publish to the DLQ.

A retry/DLQ publish must succeed **before** the retry-topic offset is
committed; a poison message (missing metadata, unmarshalable, invalid
envelope) is committed and skipped."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from pkg.emailretry import (
    DLQ_TOPIC,
    RETRY_TOPIC,
    MissingRetryMetaError,
    RetryMeta,
    build_dlq_headers,
    build_headers,
    next_retry_at,
    parse_meta,
)
from pkg.event import EmailEnvelope
from pkg.logger.logger import Logger
from service.email import metrics
from service.email.handler.email_handler import (
    InboxLike,
    MailerLike,
    RetryPublisher,
)


class RetryHandler:
    def __init__(
        self,
        logger: Logger,
        mailer: MailerLike,
        inbox: InboxLike | None,
        consumer_name: str,
        producer: RetryPublisher,
        max_retries: int,
        retry_backoff_seconds: float,
    ) -> None:
        from pkg.emailretry import DEFAULT_BACKOFF_SECONDS, DEFAULT_MAX_ATTEMPTS

        if max_retries <= 0:
            max_retries = DEFAULT_MAX_ATTEMPTS
        if retry_backoff_seconds <= 0:
            retry_backoff_seconds = DEFAULT_BACKOFF_SECONDS
        self._logger = logger
        self._mailer = mailer
        self._inbox = inbox
        self._consumer_name = consumer_name
        self._producer = producer
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff_seconds

    async def handle(self, msg: Any, commit: Any) -> None:
        try:
            meta = parse_meta(msg.headers)
        except MissingRetryMetaError as exc:
            self._logger.error(
                "Retry message without valid retry metadata; committing as poison",
                error=str(exc),
            )
            metrics.record(metrics.EMAIL_INVALID)
            await commit(msg)
            return

        # Ordered per-partition backoff: an attempt is not processed before
        # its scheduled `_retryAt` time (already capped by the backoff cap).
        now = datetime.now(UTC)
        retry_at = meta.retry_at
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=UTC)
        delay = (retry_at - now).total_seconds()
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            payload = EmailEnvelope.from_json(msg.value)
        except (TypeError, ValueError) as exc:
            self._logger.error(
                "Failed to unmarshal retry message; committing as poison",
                error=str(exc),
            )
            metrics.record(metrics.EMAIL_INVALID)
            await commit(msg)
            return
        if not payload.is_valid():
            self._logger.error(
                "Invalid email envelope in retry message; committing as poison"
            )
            metrics.record(metrics.EMAIL_INVALID)
            await commit(msg)
            return

        event_key = f"{meta.src_topic}:{payload.event_id}"
        reservation_version = 0
        if self._inbox is not None:
            reservation = await self._inbox.reserve(
                self._consumer_name,
                event_key,
                meta.src_topic,
                meta.src_partition,
                meta.src_offset,
            )
            if reservation.processed:
                # The email was already sent by an earlier attempt (or by the
                # main consumer before its offset commit) — nothing to do.
                await commit(msg)
                return
            if not reservation.reserved:
                raise RuntimeError(
                    f"consumer inbox lease is active for event {payload.event_id}"
                )
            reservation_version = reservation.reservation_version

        try:
            await self._mailer.send(payload.email, payload.subject, payload.body)
        except Exception as exc:
            self._logger.error(
                "Retry attempt failed",
                attempt=meta.attempt,
                event_key=event_key,
                error=str(exc),
            )
            metrics.record(metrics.EMAIL_FAILED)
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

            if meta.attempt >= self._max_retries:
                dlq_meta = RetryMeta(
                    src_topic=meta.src_topic,
                    src_partition=meta.src_partition,
                    src_offset=meta.src_offset,
                    attempt=meta.attempt,
                    retry_at=meta.retry_at,
                    reason=str(exc),
                    attempts=meta.attempt,
                )
                try:
                    await self._producer.send_message_with_headers(
                        DLQ_TOPIC,
                        payload.event_id,
                        msg.value,
                        build_dlq_headers(dlq_meta),
                    )
                except Exception as pub_exc:
                    raise RuntimeError(
                        f"publish to DLQ topic: {pub_exc}"
                    ) from pub_exc
                metrics.record(metrics.EMAIL_DEAD_LETTER)
                await commit(msg)
                return

            nxt = RetryMeta(
                src_topic=meta.src_topic,
                src_partition=meta.src_partition,
                src_offset=meta.src_offset,
                attempt=meta.attempt + 1,
                retry_at=next_retry_at(meta.attempt + 1, self._retry_backoff),
                reason=str(exc),
            )
            try:
                await self._producer.send_message_with_headers(
                    RETRY_TOPIC, payload.event_id, msg.value, build_headers(nxt)
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


__all__ = ["RetryHandler"]
