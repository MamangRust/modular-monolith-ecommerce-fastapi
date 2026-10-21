from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol

from pkg.logger.logger import Logger
from pkg.resilience.dependency_guard import DependencyGuard

# Project-wide defaults, matching the adapter.DefaultGuard: 5 consecutive
# failures trip the circuit breaker, which stays open for 30s, at most 100
# concurrent in-flight calls, and a 3s per-call deadline.
DEFAULT_THRESHOLD = 5
DEFAULT_BREAKER_TIMEOUT_SECS = 30.0
DEFAULT_MAX_CONCURRENT = 100
DEFAULT_CALL_TIMEOUT = 3.0


def default_guard(name: str, logger: Logger) -> DependencyGuard:
    """Build a dependency guard with the project-wide defaults."""
    return DependencyGuard(
        name,
        DEFAULT_THRESHOLD,
        DEFAULT_BREAKER_TIMEOUT_SECS,
        DEFAULT_MAX_CONCURRENT,
        DEFAULT_CALL_TIMEOUT,
        logger,
    )


class GuardSetter(Protocol):
    """Implemented by every gRPC-backed adapter so `with_dependency_guard` can attach a guard without changing each constructor's channel parameter."""

    def set_guard(self, guard: DependencyGuard | None) -> None: ...


GuardOption = Callable[[GuardSetter], None]


def with_dependency_guard(guard: DependencyGuard | None) -> GuardOption:
    """Return a GuardOption that attaches a dependency guard to a gRPC-backed adapter. Passing `None` disables guarding."""
    return lambda target: target.set_guard(guard)


async def call[T](
    guard: DependencyGuard | None,
    fn: Callable[[], Awaitable[T]],
) -> T:
    """Run `fn` under `guard` (bulkhead + circuit breaker + per-call timeout). A `None` guard runs `fn` directly."""
    if guard is None:
        return await fn()
    return await guard.call(fn)
