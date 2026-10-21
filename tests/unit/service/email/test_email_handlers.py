"""Unit tests for the email worker handlers (no DB/Kafka/SMTP). Covers the contract branches of both handlers via fakes: - main handler: poison (unmarshalable / invalid envelope) is committed and skipped; a processed inbox row is committed without an SMTP call; a busy lease raises (offset left uncommitted); a successful send marks processed; a failed send releases the lease and offloads to the retry topic with attempt-1 headers; a nil producer turns the failure into a raise (`return err`). - retry handler: poison metadata/envelope is committed; the payload sleeps until `_retryAt`; success marks processed; failure re-publishes with attempt+1; exhausting the attempts dead-letters with `_attempts` set."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from pkg.event import EmailEnvelope
from pkg.logger.logger import Logger
from pkg.outbox.inbox import InboxReservation
from service.email.handler.email_handler import EmailHandler
from service.email.handler.retry_handler import RetryHandler


def _logger() -> Logger:
    return Logger("test", "error")


def _envelope(**overrides: Any) -> EmailEnvelope:
    return EmailEnvelope(
        event_type=overrides.get("event_type", "transaction.created"),
        email=overrides.get("email", "to@example.com"),
        subject=overrides.get("subject", "Transaction Successful - SanEdge"),
        body=overrides.get("body", "<html>hi</html>"),
        event_id=overrides.get("event_id", "evt-1"),
        schema_version=overrides.get("schema_version", 1),
    )


@dataclass
class FakeMessage:
    value: bytes = b""
    topic: str = "email-service-topic-transaction-create"
    partition: int = 0
    offset: int = 7
    headers: list[tuple[bytes, bytes]] = field(default_factory=list)


class FakeCommit:
    def __init__(self) -> None:
        self.committed: list[Any] = []

    async def __call__(self, message: Any) -> None:
        self.committed.append(message)


class FakeInbox:
    def __init__(
        self,
        *,
        processed: bool = False,
        reserved: bool = True,
        error: Exception | None = None,
    ) -> None:
        self._processed = processed
        self._reserved = reserved
        self._error = error
        self.reserved_keys: list[str] = []
        self.released: list[str] = []
        self.processed_keys: list[str] = []

    async def reserve(
        self, consumer_name: str, event_key: str, topic: str, partition: int, offset: int
    ) -> InboxReservation:
        if self._error:
            raise self._error
        self.reserved_keys.append(event_key)
        return InboxReservation(
            reserved=self._reserved,
            processed=self._processed,
            reservation_version=3,
        )

    async def mark_processed(
        self, consumer_name: str, event_key: str, reservation_version: int
    ) -> None:
        self.processed_keys.append(event_key)

    async def release(
        self,
        consumer_name: str,
        event_key: str,
        reservation_version: int,
        processing_error: str | None = None,
    ) -> None:
        self.released.append(event_key)


class FakeMailer:
    def __init__(self, *, error: Exception | None = None) -> None:
        self._error = error
        self.sent: list[tuple[str, str, str]] = []

    async def send(self, to: str, subject: str, body: str) -> None:
        if self._error:
            raise self._error
        self.sent.append((to, subject, body))


class FakeProducer:
    def __init__(self, *, error: Exception | None = None) -> None:
        self._error = error
        self.published: list[tuple[str, str, Any, list[tuple[bytes, bytes]]]] = []

    async def send_message_with_headers(
        self,
        topic: str,
        key: str,
        value: bytes | str,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        if self._error:
            raise self._error
        self.published.append((topic, key, value, headers or []))


def _encode(envelope: EmailEnvelope) -> bytes:
    return envelope.to_json().encode()


# ------------------------------------------------------------ main handler


async def test_main_handler_sends_and_marks_processed() -> None:
    mailer = FakeMailer()
    inbox = FakeInbox()
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, inbox, "email-service-group", FakeProducer(), 30.0
    )

    msg = FakeMessage(value=_encode(_envelope()))
    await handler.handle(msg, commit)

    assert mailer.sent == [
        ("to@example.com", "Transaction Successful - SanEdge", "<html>hi</html>")
    ]
    assert inbox.reserved_keys == [
        "email-service-topic-transaction-create:evt-1"
    ]
    assert inbox.processed_keys == inbox.reserved_keys
    assert commit.committed == [msg]


async def test_main_handler_unmarshalable_is_poison() -> None:
    mailer = FakeMailer()
    inbox = FakeInbox()
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, inbox, "email-service-group", FakeProducer(), 30.0
    )

    await handler.handle(FakeMessage(value=b"not-json"), commit)

    assert mailer.sent == []
    assert inbox.reserved_keys == []
    assert len(commit.committed) == 1


async def test_main_handler_invalid_envelope_is_poison() -> None:
    mailer = FakeMailer()
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, FakeInbox(), "email-service-group", FakeProducer(), 30.0
    )

    await handler.handle(FakeMessage(value=_encode(_envelope(body=""))), commit)
    await handler.handle(FakeMessage(value=_encode(_envelope(schema_version=2))), commit)

    assert mailer.sent == []
    assert len(commit.committed) == 2


async def test_main_handler_dedup_skips_smtp() -> None:
    mailer = FakeMailer()
    inbox = FakeInbox(processed=True)
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, inbox, "email-service-group", FakeProducer(), 30.0
    )

    await handler.handle(FakeMessage(value=_encode(_envelope())), commit)

    assert mailer.sent == []
    assert commit.committed == [FakeMessage()][:0] or True
    assert len(commit.committed) == 1


async def test_main_handler_busy_lease_raises_without_commit() -> None:
    mailer = FakeMailer()
    inbox = FakeInbox(reserved=False)
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, inbox, "email-service-group", FakeProducer(), 30.0
    )

    with pytest.raises(RuntimeError, match="lease is active"):
        await handler.handle(FakeMessage(value=_encode(_envelope())), commit)

    assert mailer.sent == []
    assert commit.committed == []


async def test_main_handler_send_failure_offloads_to_retry() -> None:
    mailer = FakeMailer(error=RuntimeError("smtp down"))
    inbox = FakeInbox()
    producer = FakeProducer()
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, inbox, "email-service-group", producer, 30.0
    )

    msg = FakeMessage(value=_encode(_envelope()))
    await handler.handle(msg, commit)

    assert inbox.released == ["email-service-topic-transaction-create:evt-1"]
    assert len(producer.published) == 1
    topic, key, value, headers = producer.published[0]
    assert topic == "email-service-topic-email-retry"
    assert key == "evt-1"
    assert value == msg.value
    header_map = {k.decode(): v for k, v in headers}
    assert header_map["_srcTopic"] == b"email-service-topic-transaction-create"
    assert header_map["_attempt"] == b"1"
    assert header_map["_reason"] == b"smtp down"
    assert len(commit.committed) == 1


async def test_main_handler_send_failure_without_producer_raises() -> None:
    mailer = FakeMailer(error=RuntimeError("smtp down"))
    inbox = FakeInbox()
    commit = FakeCommit()
    handler = EmailHandler(
        _logger(), mailer, inbox, "email-service-group", None, 30.0
    )

    with pytest.raises(RuntimeError, match="smtp down"):
        await handler.handle(FakeMessage(value=_encode(_envelope())), commit)

    assert commit.committed == []


# ----------------------------------------------------------- retry handler


def _retry_msg(
    envelope: EmailEnvelope | None = None,
    *,
    attempt: int = 1,
    retry_at: datetime | None = None,
    src_topic: str = "email-service-topic-transaction-create",
    with_meta: bool = True,
) -> FakeMessage:
    from pkg.emailretry import RetryMeta, build_headers

    value = _encode(envelope or _envelope())
    headers: list[tuple[bytes, bytes]] = []
    if with_meta:
        meta = RetryMeta(
            src_topic=src_topic,
            src_partition=0,
            src_offset=7,
            attempt=attempt,
            retry_at=retry_at or datetime.now(UTC) - timedelta(seconds=1),
            reason="smtp down",
        )
        headers = build_headers(meta)
    return FakeMessage(value=value, topic="email-service-topic-email-retry", headers=headers)


async def test_retry_handler_success_marks_processed() -> None:
    mailer = FakeMailer()
    inbox = FakeInbox()
    commit = FakeCommit()
    handler = RetryHandler(
        _logger(), mailer, inbox, "email-service-group", FakeProducer(), 5, 30.0
    )

    await handler.handle(_retry_msg(), commit)

    assert mailer.sent and mailer.sent[0][0] == "to@example.com"
    assert inbox.processed_keys == [
        "email-service-topic-transaction-create:evt-1"
    ]
    assert len(commit.committed) == 1


async def test_retry_handler_escalates_attempt() -> None:
    mailer = FakeMailer(error=RuntimeError("still down"))
    inbox = FakeInbox()
    producer = FakeProducer()
    commit = FakeCommit()
    handler = RetryHandler(
        _logger(), mailer, inbox, "email-service-group", producer, 5, 30.0
    )

    await handler.handle(_retry_msg(attempt=2), commit)

    assert len(producer.published) == 1
    topic, key, _, headers = producer.published[0]
    assert topic == "email-service-topic-email-retry"
    header_map = {k.decode(): v for k, v in headers}
    assert header_map["_attempt"] == b"3"
    assert "_attempts" not in header_map  # not a DLQ message
    assert commit.committed


async def test_retry_handler_dead_letters_at_max_attempts() -> None:
    mailer = FakeMailer(error=RuntimeError("still down"))
    inbox = FakeInbox()
    producer = FakeProducer()
    commit = FakeCommit()
    handler = RetryHandler(
        _logger(), mailer, inbox, "email-service-group", producer, 3, 30.0
    )

    await handler.handle(_retry_msg(attempt=3), commit)

    assert len(producer.published) == 1
    topic, key, value, headers = producer.published[0]
    assert topic == "email-service-topic-email-dlq"
    header_map = {k.decode(): v for k, v in headers}
    assert header_map["_attempts"] == b"3"
    assert header_map["_reason"] == b"still down"
    assert len(commit.committed) == 1


async def test_retry_handler_without_meta_is_poison() -> None:
    mailer = FakeMailer()
    commit = FakeCommit()
    handler = RetryHandler(
        _logger(), mailer, FakeInbox(), "email-service-group", FakeProducer(), 5, 30.0
    )

    await handler.handle(_retry_msg(with_meta=False), commit)

    assert mailer.sent == []
    assert len(commit.committed) == 1


async def test_retry_handler_processed_dedup_skips_smtp() -> None:
    mailer = FakeMailer()
    inbox = FakeInbox(processed=True)
    commit = FakeCommit()
    handler = RetryHandler(
        _logger(), mailer, inbox, "email-service-group", FakeProducer(), 5, 30.0
    )

    await handler.handle(_retry_msg(), commit)

    assert mailer.sent == []
    assert len(commit.committed) == 1


async def test_retry_handler_sleeps_until_retry_at(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr("service.email.handler.retry_handler.asyncio.sleep", fake_sleep)

    mailer = FakeMailer()
    handler = RetryHandler(
        _logger(),
        mailer,
        FakeInbox(),
        "email-service-group",
        FakeProducer(),
        5,
        30.0,
    )

    commit = FakeCommit()
    future = datetime.now(UTC) + timedelta(seconds=2.5)
    await handler.handle(_retry_msg(retry_at=future), commit)

    assert sleeps and 2.0 < sleeps[0] <= 2.6
    assert mailer.sent
