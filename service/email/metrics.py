"""Email service OTel counters.

Counters are created lazily from the global meter. `register` must run
*after* the OTel SDK is initialised: an instrument created before the meter
provider is installed binds to the API's no-op meter and every `add` on it
is discarded, so the series exports as 0 forever."""

from __future__ import annotations

from typing import Any

# Populated by `register()`; kept as module globals so call sites can keep
# referring to `metrics.EMAIL_SENT` and friends.
EMAIL_SENT: Any = None
EMAIL_FAILED: Any = None
EMAIL_INVALID: Any = None
EMAIL_RETRIED: Any = None
EMAIL_DEAD_LETTER: Any = None


def _counter(meter: Any, name: str, description: str) -> Any:
    return meter.create_counter(name, unit="1", description=description)


def register() -> None:
    """Create the counters from the global meter (call after SDK init)."""
    global EMAIL_SENT, EMAIL_FAILED, EMAIL_INVALID, EMAIL_RETRIED, EMAIL_DEAD_LETTER

    from opentelemetry import metrics as otel_metrics

    meter = otel_metrics.get_meter("email-service")
    EMAIL_SENT = _counter(meter, "email_sent_total", "Total emails sent successfully")
    EMAIL_FAILED = _counter(meter, "email_failed_total", "Total emails failed")
    EMAIL_INVALID = _counter(
        meter,
        "email_invalid_total",
        "Total malformed or unprocessable Kafka messages",
    )
    EMAIL_RETRIED = _counter(
        meter,
        "email_retried_total",
        "Total emails published to the retry topic after a transient SMTP failure",
    )
    EMAIL_DEAD_LETTER = _counter(
        meter,
        "email_deadletter_total",
        "Total emails dead-lettered after exhausting retries",
    )


def record(counter: Any, status: str = "") -> None:
    """Add 1 to `counter`; a no-op before `register` has run."""
    if counter is None:
        return
    if status:
        counter.add(1, {"status": status})
    else:
        counter.add(1)


__all__ = [
    "EMAIL_DEAD_LETTER",
    "EMAIL_FAILED",
    "EMAIL_INVALID",
    "EMAIL_RETRIED",
    "EMAIL_SENT",
    "record",
    "register",
]
