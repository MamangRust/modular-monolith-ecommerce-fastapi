"""Unit tests for pkg.resilience.circuit_breaker."""

from pkg.logger.logger import Logger
from pkg.resilience.circuit_breaker import CircuitBreaker


def _breaker(threshold: int = 3, timeout_secs: float = 30.0) -> CircuitBreaker:
    return CircuitBreaker(threshold, timeout_secs, Logger("test", "error"))


async def test_allows_requests_while_closed() -> None:
    cb = _breaker()
    assert cb.should_allow_request()
    assert not cb.is_open()


async def test_opens_after_threshold_consecutive_failures() -> None:
    cb = _breaker(threshold=3)
    cb.record_failure()
    cb.record_failure()
    assert not cb.is_open()
    assert cb.should_allow_request()

    cb.record_failure()
    assert cb.is_open()
    assert not cb.should_allow_request()


async def test_success_resets_failure_count() -> None:
    cb = _breaker(threshold=3)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb.get_failure_count() == 0

    cb.record_failure()
    cb.record_failure()
    assert not cb.is_open()


async def test_half_open_allows_probe_after_timeout() -> None:
    cb = _breaker(threshold=1, timeout_secs=0.05)
    cb.record_failure()
    assert cb.is_open()
    assert not cb.should_allow_request()

    import asyncio

    await asyncio.sleep(0.06)
    assert cb.should_allow_request()


async def test_half_open_successes_close_the_circuit() -> None:
    cb = _breaker(threshold=1, timeout_secs=0.0)
    cb.record_failure()
    assert cb.is_open()

    for _ in range(5):
        assert cb.should_allow_request()
        cb.record_success()
    assert not cb.is_open()
    assert cb.get_failure_count() == 0
    assert cb.get_success_count() == 0


async def test_reset_closes_the_circuit() -> None:
    cb = _breaker(threshold=1)
    cb.record_failure()
    assert cb.is_open()
    cb.reset()
    assert not cb.is_open()
    assert cb.should_allow_request()
