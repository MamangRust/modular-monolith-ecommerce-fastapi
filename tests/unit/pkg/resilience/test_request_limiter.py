"""Unit tests for pkg.resilience.request_limiter (the bulkhead)."""

from pkg.logger.logger import Logger
from pkg.resilience.request_limiter import RequestLimiter


def _limiter(max_concurrent: int) -> RequestLimiter:
    return RequestLimiter(max_concurrent, Logger("test", "error"))


async def test_acquire_and_release_roundtrip() -> None:
    limiter = _limiter(2)
    assert limiter.try_acquire()
    assert limiter.in_flight == 1
    assert limiter.available_permits == 1

    limiter.release()
    assert limiter.in_flight == 0
    assert limiter.available_permits == 2


async def test_refuses_when_full() -> None:
    limiter = _limiter(1)
    assert limiter.try_acquire()
    assert not limiter.try_acquire()
    limiter.release()
    assert limiter.try_acquire()


async def test_release_below_zero_clamps_to_zero() -> None:
    limiter = _limiter(2)
    limiter.release()
    assert limiter.in_flight == 0


async def test_non_positive_max_concurrent_defaults_to_100() -> None:
    limiter = _limiter(0)
    assert limiter.max_concurrent == 100
