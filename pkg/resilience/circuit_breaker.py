"""Circuit breaker. Counts consecutive failures and opens after `threshold` in a row. While open every request is refused until `timeout` seconds have passed since the last failure; then up to `half_open_max_requests` probe requests (half-open state) decide recovery — that many successes close the circuit again. the version guards its fields with atomics because gRPC handlers run on many goroutines; runs on a single asyncio event loop, so the plain attributes below are already race-free."""

from __future__ import annotations

import time

from pkg.logger.logger import Logger

_HALF_OPEN_MAX_REQUESTS = 5


class CircuitBreaker:
    """CircuitBreaker."""

    def __init__(self, threshold: int, timeout_secs: float, logger: Logger) -> None:
        self._threshold = threshold
        self._timeout = timeout_secs
        self._logger = logger
        self._failure_count = 0
        self._success_count = 0
        self._is_open = False
        self._last_failure_time = 0.0

    def is_open(self) -> bool:
        return self._is_open

    def get_failure_count(self) -> int:
        return self._failure_count

    def get_success_count(self) -> int:
        return self._success_count

    def should_allow_request(self) -> bool:
        if not self._is_open:
            return True

        if time.monotonic() - self._last_failure_time <= self._timeout:
            return False

        self._logger.info("Circuit breaker timeout passed, entering half-open state")
        if self._success_count < _HALF_OPEN_MAX_REQUESTS:
            return True

        self.close_circuit()
        return True

    def record_success(self) -> None:
        self._success_count += 1
        if self._is_open and self._success_count >= _HALF_OPEN_MAX_REQUESTS:
            self.close_circuit()
        self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self._threshold and not self._is_open:
            self.open_circuit()

    def open_circuit(self) -> None:
        self._logger.warn(
            "Circuit breaker opened", failures=self.get_failure_count()
        )
        self._is_open = True
        self._success_count = 0
        self._last_failure_time = time.monotonic()

    def close_circuit(self) -> None:
        self._logger.info("Circuit breaker closed - service recovered")
        self._is_open = False
        self._failure_count = 0
        self._success_count = 0

    def reset(self) -> None:
        self.close_circuit()
