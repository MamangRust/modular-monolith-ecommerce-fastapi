"""Email worker integration tests against a real PostgreSQL. Marked `integration`. Kafka and SMTP stay faked — what the database is for here is the **consumer inbox**: reservation/lease semantics, dedup across redelivery, and release-on-failure, exercised through the real `PostgresInbox` and the real `EmailHandler` (the contract's whole point is that the side effect dedup survives restarts). Each test uses a unique consumer/event key and removes its inbox rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from pkg.database.database import Database
from pkg.event import EmailEnvelope
from pkg.logger.logger import Logger
from pkg.outbox.inbox import PostgresInbox
from service.email.handler.email_handler import EmailHandler

pytestmark = pytest.mark.integration


def _logger() -> Logger:
    return Logger("test", "error")


def _envelope(event_id: str) -> EmailEnvelope:
    return EmailEnvelope(
        event_type="transaction.created",
        email="to@example.com",
        subject="Transaction Successful - SanEdge",
        body="<html>hi</html>",
        event_id=event_id,
        schema_version=1,
    )


@dataclass
class FakeMessage:
    value: bytes
    topic: str = "email-service-topic-transaction-create"
    partition: int = 0
    offset: int = 7
    headers: list[tuple[bytes, bytes]] | None = None


class FakeCommit:
    def __init__(self) -> None:
        self.committed: list[Any] = []

    async def __call__(self, message: Any) -> None:
        self.committed.append(message)


class FakeMailer:
    def __init__(self, *, error: Exception | None = None) -> None:
        self._error = error
        self.sent: list[tuple[str, str, str]] = []

    async def send(self, to: str, subject: str, body: str) -> None:
        if self._error:
            raise self._error
        self.sent.append((to, subject, body))


class FakeProducer:
    def __init__(self) -> None:
        self.published: list[tuple[str, str, Any, list[tuple[bytes, bytes]]]] = []

    async def send_message_with_headers(
        self,
        topic: str,
        key: str,
        value: bytes | str,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        self.published.append((topic, key, value, headers or []))


@pytest.fixture
async def inbox(db: Database) -> PostgresInbox:
    return PostgresInbox(db)


async def _cleanup_inbox(db: Database, consumer: str) -> None:
    await db.execute(
        "DELETE FROM consumer_inbox WHERE consumer_name = :c", {"c": consumer}
    )


async def test_inbox_reserve_process_dedup_flow(db: Database, inbox) -> None:
    consumer = "email-service-group-itest-a"
    event_key = "email-service-topic-transaction-create:evt-a"
    try:
        first = await inbox.reserve(consumer, event_key, "topic", 0, 1)
        assert first.reserved is True
        assert first.processed is False

        # A redelivery while the lease is active cannot re-reserve.
        second = await inbox.reserve(consumer, event_key, "topic", 0, 1)
        assert second.reserved is False
        assert second.processed is False

        await inbox.mark_processed(consumer, event_key, first.reservation_version)

        # After processing, any redelivery is a dedup hit.
        third = await inbox.reserve(consumer, event_key, "topic", 0, 1)
        assert third.processed is True
    finally:
        await _cleanup_inbox(db, consumer)


async def test_inbox_release_allows_reclaim(db: Database, inbox) -> None:
    consumer = "email-service-group-itest-b"
    event_key = "email-service-topic-transaction-create:evt-b"
    try:
        first = await inbox.reserve(consumer, event_key, "topic", 0, 2)
        await inbox.release(consumer, event_key, first.reservation_version, "smtp down")

        row = await db.execute(
            "SELECT status, last_error FROM consumer_inbox "
            "WHERE consumer_name = :c AND event_key = :k",
            {"c": consumer, "k": event_key},
        )
        assert row is not None
        assert row["status"] == "pending"
        assert row["last_error"] == "smtp down"

        # The released lease can be reclaimed immediately (new version).
        again = await inbox.reserve(consumer, event_key, "topic", 0, 2)
        assert again.reserved is True
        assert again.reservation_version > first.reservation_version
    finally:
        await _cleanup_inbox(db, consumer)


async def test_email_handler_dedup_survives_redelivery(
    db: Database, inbox
) -> None:
    consumer = "email-service-group-itest-c"
    mailer = FakeMailer()
    producer = FakeProducer()
    handler = EmailHandler(_logger(), mailer, inbox, consumer, producer, 30.0)
    event_id = "evt-c"
    envelope = _envelope(event_id)
    try:
        commit = FakeCommit()
        await handler.handle(FakeMessage(value=envelope.to_json().encode()), commit)
        assert len(mailer.sent) == 1
        assert len(commit.committed) == 1

        # The offset was committed, but imagine the worker died before it:
        # a redelivery of the same event must NOT resend the email.
        redelivered = FakeCommit()
        await handler.handle(
            FakeMessage(
                value=envelope.to_json().encode(), offset=8
            ),
            redelivered,
        )
        assert len(mailer.sent) == 1  # dedup, not a second send
        assert len(redelivered.committed) == 1
        assert producer.published == []
    finally:
        await _cleanup_inbox(db, consumer)


async def test_email_handler_failure_releases_and_offloads(
    db: Database, inbox
) -> None:
    consumer = "email-service-group-itest-d"
    mailer = FakeMailer(error=RuntimeError("smtp down"))
    producer = FakeProducer()
    handler = EmailHandler(_logger(), mailer, inbox, consumer, producer, 30.0)
    event_id = "evt-d"
    try:
        commit = FakeCommit()
        message = FakeMessage(value=_envelope(event_id).to_json().encode())
        await handler.handle(message, commit)

        assert mailer.sent == []
        assert len(producer.published) == 1
        topic, key, value, headers = producer.published[0]
        assert topic == "email-service-topic-email-retry"
        assert key == event_id
        assert value == message.value
        header_map = {k.decode(): v for k, v in headers}
        assert header_map["_srcTopic"] == b"email-service-topic-transaction-create"
        assert header_map["_attempt"] == b"1"
        assert len(commit.committed) == 1

        # The inbox row was released (pending + last_error), so a later retry
        # attempt can reclaim the lease.
        row = await db.execute(
            "SELECT status, last_error FROM consumer_inbox "
            "WHERE consumer_name = :c AND event_key = :k",
            {"c": consumer, "k": f"email-service-topic-transaction-create:{event_id}"},
        )
        assert row is not None
        assert row["status"] == "pending"
        assert row["last_error"] == "smtp down"
    finally:
        await _cleanup_inbox(db, consumer)
