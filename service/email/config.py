"""Email service configuration. SMTP/limits come from the shared `SmtpSettings` (the `SMTP_HOST` naming stands in for `SMTP_SERVER`; see the)."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.config.settings import Settings, get_settings
from pkg.emailretry import DEFAULT_BACKOFF_SECONDS, DEFAULT_MAX_ATTEMPTS


@dataclass(frozen=True)
class EmailConfig:
    kafka_brokers: list[str]
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    # MaxRetries is the number of SMTP attempts (including the first) before
    # an event is dead-lettered.
    max_retries: int
    # RetryBackoff is the base delay before the next attempt; the actual delay
    # grows linearly with the attempt number (emailretry.backoff).
    retry_backoff_seconds: float


def new_config(settings: Settings | None = None) -> EmailConfig:
    resolved = settings or get_settings()
    smtp = resolved.smtp
    max_retries = smtp.max_retries if smtp.max_retries > 0 else DEFAULT_MAX_ATTEMPTS
    retry_backoff = (
        smtp.retry_backoff_seconds
        if smtp.retry_backoff_seconds > 0
        else DEFAULT_BACKOFF_SECONDS
    )
    return EmailConfig(
        kafka_brokers=resolved.kafka.broker_list,
        smtp_server=smtp.smtp_host,
        smtp_port=smtp.smtp_port,
        smtp_user=smtp.smtp_user,
        smtp_pass=smtp.smtp_password,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff,
    )


__all__ = ["EmailConfig", "new_config"]
