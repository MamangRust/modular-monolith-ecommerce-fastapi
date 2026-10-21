"""Bulkhead / request limiter. Caps the number of concurrent in-flight calls to one dependency. `try_acquire` refuses instead of waiting — a saturated dependency sheds load immediately rather than queueing. the version wraps a weighted semaphore; on a single asyncio event loop a plain counter is equivalent and race-free."""

from __future__ import annotations

from pkg.logger.logger import Logger

_DEFAULT_MAX_CONCURRENT = 100


class RequestLimiter:
    """RequestLimiter."""

    def __init__(self, max_concurrent: int, logger: Logger) -> None:
        if max_concurrent <= 0:
            logger.warn(
                "RequestLimiter maxConcurrent must be positive, defaulting to 100",
                provided=max_concurrent,
            )
            max_concurrent = _DEFAULT_MAX_CONCURRENT

        self._max_concurrent = max_concurrent
        self._logger = logger
        self._in_flight = 0

    def try_acquire(self) -> bool:
        if self._in_flight >= self._max_concurrent:
            return False
        self._in_flight += 1
        return True

    def release(self) -> None:
        self._in_flight -= 1
        if self._in_flight < 0:
            self._logger.error(
                "RequestLimiter: Released more permits than were acquired",
                in_flight=self._in_flight,
                max_concurrent=self._max_concurrent,
            )
            self._in_flight = 0

    @property
    def available_permits(self) -> int:
        return self._max_concurrent - self._in_flight

    @property
    def max_concurrent(self) -> int:
        return self._max_concurrent

    @property
    def in_flight(self) -> int:
        return self._in_flight
