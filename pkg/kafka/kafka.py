"""Kafka producer/consumer. - SendMessageWithRetry: linear backoff 200ms*(i+1). - background reconnect loop: max 5 consecutive consume-loop failures, 30s between retries; consumer errors are logged, not raised."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.structs import TopicPartition

from pkg.logger.logger import Logger


class ConsumerCloser(Protocol):
    async def close(self) -> None: ...


HandlerCallback = Callable[[Any, Callable[[Any], Awaitable[None]]], Awaitable[None]]


class RoleKafkaHandlerLike(Protocol):
    """Shape of the aiokafka handler callbacks used by our consumers."""

    async def __call__(
        self, msg: Any, commit: Callable[[Any], Awaitable[None]]
    ) -> None: ...


class Kafka:
    def __init__(
        self,
        logger: Logger,
        brokers: list[str],
        producer: AIOKafkaProducer | None = None,
    ) -> None:
        self._logger = logger
        self._brokers = brokers
        self._producer = producer or AIOKafkaProducer(
            bootstrap_servers=",".join(brokers),
            acks="all",
            max_batch_size=1_048_576,
            max_request_size=1_048_576,
        )
        self._owns_producer = producer is None
        self._consumers: list[AsyncManagedConsumer] = []
        self._closed = False

    @property
    def brokers(self) -> list[str]:
        return list(self._brokers)

    async def start(self) -> None:
        if self._owns_producer:
            await self._producer.start()
        self._logger.info("kafka producer connected", brokers=",".join(self._brokers))

    async def send_message(self, topic: str, key: str, value: bytes | str) -> None:
        payload = value.encode("utf-8") if isinstance(value, str) else value
        await self._producer.send_and_wait(topic, key=key.encode("utf-8") if key else None, value=payload)

    async def send_message_with_headers(
        self,
        topic: str,
        key: str,
        value: bytes | str,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        """Publish with record headers (retry/DLQ metadata, `SendMessageWithHeaders`)."""
        payload = value.encode("utf-8") if isinstance(value, str) else value
        await self._producer.send_and_wait(
            topic,
            key=key.encode("utf-8") if key else None,
            value=payload,
            headers=list(headers or ()),
        )

    async def send_message_with_retry(
        self, topic: str, key: str, value: bytes | str, attempts: int
    ) -> None:
        last_error: Exception | None = None
        for i in range(attempts):
            try:
                await self.send_message(topic, key, value)
                return
            except Exception as exc:
                last_error = exc
                if i < attempts - 1:
                    await asyncio.sleep(0.2 * (i + 1))
        if last_error is not None:
            raise last_error

    async def start_consumers(
        self,
        topics: list[str],
        group_id: str,
        handler: RoleKafkaHandlerLike,
        manual_commit: bool = False,
    ) -> AsyncManagedConsumer:
        consumer = AsyncManagedConsumer(
            logger=self._logger,
            brokers=self._brokers,
            topics=topics,
            group_id=group_id,
            handler=handler,
            manual_commit=manual_commit,
        )
        self._consumers.append(consumer)
        await consumer.start()
        return consumer

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for consumer in self._consumers:
            await consumer.close()
        if self._owns_producer:
            await self._producer.stop()
        self._logger.info("kafka resources closed")


@dataclass
class AsyncManagedConsumer:
    """`handler(msg, commit)` is called per message. In auto-commit mode the offset is advanced automatically; in manual-commit mode the handler must call `await commit(msg)` only after reaching a terminal outcome, so a failed side effect leaves the offset uncommitted and is redelivered."""

    logger: Logger
    brokers: list[str]
    topics: list[str]
    group_id: str
    handler: HandlerCallback
    manual_commit: bool = False

    def __post_init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()
        self._closed_once = False
        self._close_error: BaseException | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run_loop())

    def _new_consumer(self) -> AIOKafkaConsumer:
        kwargs: dict[str, Any] = {
            "bootstrap_servers": ",".join(self.brokers),
            "group_id": self.group_id,
            "enable_auto_commit": not self.manual_commit,
            "auto_offset_reset": "earliest",
        }
        return AIOKafkaConsumer(*self.topics, **kwargs)

    async def _run_loop(self) -> None:
        retries = 0
        max_retries = 5
        while not self._stopping.is_set():
            consumer = self._new_consumer()
            self._consumer = consumer
            try:
                await consumer.start()
            except Exception as exc:
                self.logger.error("kafka consumer start failed", error=str(exc))
                await self._backoff()
                continue
            try:
                async for msg in consumer:
                    commit = self._make_commit(consumer, msg)
                    try:
                        await self.handler(msg, commit)
                    except Exception as exc:
                        self.logger.error(
                            "kafka message processing failed; offset left uncommitted",
                            topic=msg.topic,
                            partition=msg.partition,
                            offset=msg.offset,
                            error=str(exc),
                        )
                        # In auto-commit mode aiokafka still advances the offset;
                        # to honour "leave uncommitted" semantics we stop the
                        # consumer so the loop restarts and redelivers.
                        raise
            except asyncio.CancelledError:
                break
            except Exception:
                retries += 1
                if retries >= max_retries:
                    self.logger.error("kafka consumer max retries reached; stopping")
                    break
                await self._backoff()
            else:
                retries = 0
            finally:
                try:
                    await consumer.stop()
                except Exception:
                    pass
            self._consumer = None
            if self._stopping.is_set():
                break
            await self._backoff()

    def _make_commit(self, consumer: AIOKafkaConsumer, msg: Any) -> Callable[[Any], Awaitable[None]]:
        """Build the per-message `commit` callback handed to the handler. aiokafka's `commit` takes a `{TopicPartition: next_offset}` mapping (or `None` for "everything consumed so far") — not the message itself. Forwarding the `ConsumerRecord` makes `commit_structure_validate` raise `ValueError(record)`, so a manual-commit consumer can never advance its offset: every message fails, is redelivered, and the consume loop keeps restarting. Commit next-offset, per aiokafka's documented usage."""

        async def _commit(message: Any) -> None:
            if self.manual_commit:
                tp = TopicPartition(message.topic, message.partition)
                await consumer.commit({tp: message.offset + 1})

        return _commit

    async def _backoff(self) -> None:
        for _ in range(30):
            if self._stopping.is_set():
                return
            await asyncio.sleep(1)

    async def close(self) -> None:
        if self._closed_once:
            return
        self._closed_once = True
        self._stopping.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await asyncio.wait_for(asyncio.shield(self._task), timeout=5.0)
            except (TimeoutError, asyncio.CancelledError, Exception) as exc:
                self._close_error = exc
        # `_run_loop` stops the consumer in its own `finally`, but a cancellation
        # delivered while the consumer was still starting (e.g. blocked fetching
        # topic metadata) never reaches that block, leaving the aiokafka consumer
        # open. Stop it here too, otherwise aiokafka warns
        # "Unclosed AIOKafkaConsumer" at interpreter exit.
        if self._consumer is not None:
            try:
                await self._consumer.stop()
            except Exception as exc:
                self._close_error = exc
