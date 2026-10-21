"""Value conversion helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Any

from google.protobuf.wrappers_pb2 import StringValue

DATE_FMT = "%Y-%m-%d"  # wire format used by the gRPC handlers
RFC3339_FMT = "%Y-%m-%dT%H:%M:%SZ"
TIME_FMT = "%Y-%m-%d %H:%M:%S"  # FormatTimePtr ("2006-01-02 15:04:05")
MILLIS_FMT = "%Y-%m-%d %H:%M:%S.%f"  # "2006-01-02 15:04:05.000"
CLOCK_FMT = "%H:%M:%S"  # banner formatTime ("15:04:05")


def format_date(ts: datetime | None) -> str:
    """Naive timestamps from PG are treated as UTC."""
    if ts is None:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.strftime(DATE_FMT)


def format_iso_date(value: date | None) -> str:
    """Format a plain DATE value (no timezone bookkeeping)."""
    return value.strftime(DATE_FMT) if value is not None else ""


def format_timestamp_millis(ts: datetime | None) -> str:
    """layout `2006-01-02 15:04:05.000` prints exactly three fractional digits; Python's `%f` prints six, so the result is truncated to 23 characters."""
    if ts is None:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.strftime(MILLIS_FMT)[:23]


def format_clock(value: time | None) -> str:
    return value.strftime(CLOCK_FMT) if value is not None else ""


def format_time_ptr(ts: datetime | None) -> str:
    if ts is None:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.strftime(TIME_FMT)


def format_time_rfc3339(ts: datetime | None) -> str:
    if ts is None:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.strftime(RFC3339_FMT)


def str_val(value: str | None) -> str:
    return value or ""


def int32_val(value: int | None) -> int:
    return 0 if value is None else value


def time_to_wrappers(ts: datetime | None) -> StringValue | None:
    formatted = format_time_rfc3339(ts)
    if not formatted:
        return None
    return StringValue(value=formatted)


def first_total(rows: list[dict[str, Any]] | list[Any]) -> int:
    """COUNT(*) OVER is repeated on every row; take the first row's value."""
    if not rows:
        return 0
    row = rows[0]
    total = getattr(row, "total_count", None)
    if total is None and isinstance(row, dict):
        total = row.get("total_count")
    return int(total or 0)
