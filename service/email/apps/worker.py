"""Email worker composition. Not a gRPC service: the worker starts two Kafka consumer groups — - `email-service-group` on the eight outbox email topics (auth x3, merchant x4, transaction x1), manual commit; - `email-service-retry-group` on the shared retry topic, manual commit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pkg.config.settings import Settings, get_settings
from pkg.emailretry import DLQ_TOPIC, RETRY_GROUP, RETRY_TOPIC
from pkg.kafka.kafka import Kafka
from pkg.logger.logger import Logger, get_logger
from pkg.otel import Telemetry, TelemetryConfig
from pkg.outbox.inbox import PostgresInbox
from service.email import metrics as email_metrics
from service.email.config import new_config
from service.email.handler.email_handler import (
    CONSUMER_GROUP,
    EmailHandler,
)
from service.email.handler.retry_handler import RetryHandler
from service.email.mailer.smtp import Mailer

# The eight outbox email topics produced by auth (3), merchant (4) and
EMAIL_TOPICS: tuple[str, ...] = (
    "email-service-topic-auth-register",
    "email-service-topic-auth-forgot-password",
    "email-service-topic-auth-verify-code-success",
    "email-service-topic-merchant-create",
    "email-service-topic-merchant-update-status",
    "email-service-topic-merchant-document-create",
    "email-service-topic-merchant-document-update-status",
    "email-service-topic-transaction-create",
)

SERVICE_NAME = "email-service"


@dataclass(frozen=True)
class EmailWorker:
    kafka: Kafka
    main_consumer: Any
    retry_consumer: Any
    telemetry: Any

    async def close(self) -> None:
        await self.kafka.close()
        if self.telemetry is not None:
            await self.telemetry.shutdown()


async def new_worker(
    settings: Settings | None = None, logger: Logger | None = None
) -> EmailWorker:
    resolved = settings or get_settings()
    log = logger or get_logger(SERVICE_NAME)
    cfg = new_config(resolved)

    telemetry = Telemetry(
        TelemetryConfig(
            service_name=SERVICE_NAME,
            environment=resolved.app.env,
            endpoint=resolved.app.otel_endpoint,
            insecure=True,
            enabled=resolved.app.otel_enabled,
        ),
        log,
    )
    telemetry.init()

    # Bind the email counters to the real meter provider (see metrics module).
    email_metrics.register()

    from pkg.database.database import Database

    db = Database.create(resolved.database, log)
    await db.ping()

    inbox = PostgresInbox(db)

    mailer = Mailer(cfg.smtp_server, cfg.smtp_port, cfg.smtp_user, cfg.smtp_pass)

    kafka = Kafka(log, cfg.kafka_brokers)
    await kafka.start()

    email_handler = EmailHandler(
        log,
        mailer,
        inbox,
        CONSUMER_GROUP,
        kafka,
        cfg.retry_backoff_seconds,
    )
    main_consumer = await kafka.start_consumers(
        list(EMAIL_TOPICS),
        CONSUMER_GROUP,
        email_handler.handle,
        manual_commit=True,
    )

    retry_handler = RetryHandler(
        log,
        mailer,
        inbox,
        CONSUMER_GROUP,
        kafka,
        cfg.max_retries,
        cfg.retry_backoff_seconds,
    )
    retry_consumer = await kafka.start_consumers(
        [RETRY_TOPIC],
        RETRY_GROUP,
        retry_handler.handle,
        manual_commit=True,
    )

    log.info(
        "Email service started",
        retry_topic=RETRY_TOPIC,
        dlq_topic=DLQ_TOPIC,
    )
    return EmailWorker(
        kafka=kafka,
        main_consumer=main_consumer,
        retry_consumer=retry_consumer,
        telemetry=telemetry,
    )


__all__ = ["EMAIL_TOPICS", "SERVICE_NAME", "EmailWorker", "new_worker"]
