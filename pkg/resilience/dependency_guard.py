"""Dependency guard. Wraps outbound calls to one remote dependency with a bulkhead (RequestLimiter), a circuit breaker and a per-call timeout, so a failing or slow dependency is refused locally instead of piling up requests. A `None` guard is a valid passthrough — handled in `pkg.adapter.guard.call`, which is what adapters use, so adapters keep working when no guard is attached."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from pkg.logger.logger import Logger
from pkg.resilience.circuit_breaker import CircuitBreaker
from pkg.resilience.request_limiter import RequestLimiter

T = TypeVar("T")


class DependencyGuardOpenError(Exception):
    """The circuit breaker is open and refused to forward the call."""


class DependencyGuardBulkheadError(Exception):
    """The concurrent request limit for this dependency has been reached."""


class DependencyGuard:
    """DependencyGuard."""

    def __init__(
        self,
        name: str,
        threshold: int,
        breaker_timeout_secs: float,
        max_concurrent: int,
        call_timeout: float,
        logger: Logger,
    ) -> None:
        self._name = name
        self._limiter = RequestLimiter(max_concurrent, logger)
        self._breaker = CircuitBreaker(threshold, breaker_timeout_secs, logger)
        self._timeout = call_timeout
        self._logger = logger

    @property
    def name(self) -> str:
        """The dependency name the guard was built with."""
        return self._name

    async def call(self, fn: Callable[[], Awaitable[T]]) -> T:
        """Run `fn` guarded by the bulkhead, circuit breaker and timeout."""
        return await self.call_with_outcome(fn, None)

    async def call_with_outcome(
        self,
        fn: Callable[[], Awaitable[T]],
        is_failure: Callable[[Exception], bool] | None,
    ) -> T:
        """Like `call`, but only records a failure when `is_failure` says so. A `None` `is_failure` counts every exception as a failure (with CallWithOutcome(nil)."""
        if not self._breaker.should_allow_request():
            self._logger.warn(
                "Dependency guard: circuit breaker open, rejecting call",
                dependency=self._name,
            )
            raise DependencyGuardOpenError(
                "dependency guard: circuit breaker is open"
            )

        if not self._limiter.try_acquire():
            self._logger.warn(
                "Dependency guard: bulkhead full, rejecting call",
                dependency=self._name,
            )
            raise DependencyGuardBulkheadError(
                "dependency guard: too many concurrent requests"
            )

        try:
            try:
                if self._timeout > 0:
                    async with asyncio.timeout(self._timeout):
                        result = await fn()
                else:
                    result = await fn()
            except Exception as err:
                if is_failure is None or is_failure(err):
                    self._breaker.record_failure()
                else:
                    self._breaker.record_success()
                raise

            self._breaker.record_success()
            return result
        finally:
            self._limiter.release()
