
import asyncio

import pytest

from pkg.logger.logger import Logger
from pkg.resilience.dependency_guard import (
    DependencyGuard,
    DependencyGuardBulkheadError,
    DependencyGuardOpenError,
)


def _guard(
    threshold: int = 3,
    max_concurrent: int = 10,
    call_timeout: float = 0.0,
) -> DependencyGuard:
    return DependencyGuard(
        "dep", threshold, 30.0, max_concurrent, call_timeout, Logger("test", "error")
    )


async def test_success_passes_result_through() -> None:
    guard = _guard()

    async def fn() -> str:
        return "ok"

    assert await guard.call(fn) == "ok"
    assert guard._breaker.get_failure_count() == 0


async def test_exception_is_reraised_and_recorded_as_failure() -> None:
    guard = _guard(threshold=5)

    async def boom() -> None:
        raise RuntimeError("downstream down")

    with pytest.raises(RuntimeError, match="downstream down"):
        await guard.call(boom)
    assert guard._breaker.get_failure_count() == 1


async def test_opens_after_threshold_and_refuses_without_calling() -> None:
    guard = _guard(threshold=3)
    calls = 0

    async def boom() -> None:
        nonlocal calls
        calls += 1
        raise RuntimeError("x")

    for _ in range(3):
        with pytest.raises(RuntimeError):
            await guard.call(boom)

    with pytest.raises(DependencyGuardOpenError):
        await guard.call(boom)
    assert calls == 3


async def test_bulkhead_rejects_when_concurrency_exhausted() -> None:
    guard = _guard(max_concurrent=1)
    release = asyncio.Event()

    async def wait_for_release() -> str:
        await release.wait()
        return "done"

    first = asyncio.ensure_future(guard.call(wait_for_release))
    await asyncio.sleep(0)

    async def never() -> str:
        raise AssertionError("must not run")

    with pytest.raises(DependencyGuardBulkheadError):
        await guard.call(never)

    release.set()
    assert await first == "done"


async def test_call_timeout_enforced() -> None:
    guard = _guard(call_timeout=0.05)

    async def slow() -> str:
        await asyncio.sleep(1.0)
        return "late"

    with pytest.raises(TimeoutError):
        await guard.call(slow)
    assert guard._breaker.get_failure_count() == 1


async def test_call_with_outcome_ignores_classified_ok_errors() -> None:
    guard = _guard(threshold=2)

    async def business_error() -> None:
        raise ValueError("not a dependency problem")

    for _ in range(5):
        with pytest.raises(ValueError):
            await guard.call_with_outcome(business_error, lambda err: False)

    assert not guard._breaker.is_open()


async def test_call_with_outcome_none_counts_every_error() -> None:
    guard = _guard(threshold=1)

    async def boom() -> None:
        raise ValueError("x")

    with pytest.raises(ValueError):
        await guard.call_with_outcome(boom, None)
    assert guard._breaker.is_open()


async def test_bulkhead_released_when_fn_raises() -> None:
    guard = _guard(max_concurrent=1)

    async def boom() -> None:
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        await guard.call(boom)

    async def fine() -> str:
        return "ok"

    assert await guard.call(fine) == "ok"
    assert guard._limiter.in_flight == 0
