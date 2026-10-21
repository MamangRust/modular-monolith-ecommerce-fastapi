"""Per-method dependency guard interceptor. Applies a DependencyGuard (circuit breaker + bulkhead + per-call deadline) to every unary gRPC call made through the channel it is attached to. Guards are keyed by the full method name ("/package.Service/Method") so each downstream dependency has its own breaker and bulkhead: one slow or failing dependency cannot exhaust the caller's concurrency or open the circuit for unrelated services. The per-call deadline is enforced natively by shrinking `client_call_details.timeout` to the guard's deadline — a deadline hit then surfaces as a regular AioRpcError(DEADLINE_EXCEEDED). Rejected calls are mapped to gRPC status codes like guard_dial_option.— Unavailable when the breaker is open, ResourceExhausted when the bulkhead is full — so downstream error parsing treats them like any other failed call. Usage: channel = grpc.aio.insecure_channel(address, options=_CHANNEL_OPTIONS, interceptors=[DependencyGuardInterceptor(logger)],)"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import grpc
import grpc.aio as grpc_aio

from pkg.logger.logger import Logger
from pkg.resilience.dependency_guard import (
    DependencyGuard,
    DependencyGuardBulkheadError,
    DependencyGuardOpenError,
)

_DEFAULT_THRESHOLD = 5
_DEFAULT_BREAKER_TIMEOUT_SECS = 30.0
_DEFAULT_MAX_CONCURRENT = 100
_DEFAULT_CALL_TIMEOUT = 3.0


class DependencyGuardInterceptor(grpc_aio.UnaryUnaryClientInterceptor):
    """DependencyGuardInterceptor. Safe for concurrent use by many coroutines: guard creation only happens on the event loop thread and the guards themselves are loop-confined."""

    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._guards: dict[str, DependencyGuard] = {}

    def _guard_for(self, method: str) -> DependencyGuard:
        guard = self._guards.get(method)
        if guard is None:
            # Per-call timeout is enforced through the RPC deadline below, so
            # the guard itself runs without a second asyncio.timeout.
            guard = DependencyGuard(
                method,
                _DEFAULT_THRESHOLD,
                _DEFAULT_BREAKER_TIMEOUT_SECS,
                _DEFAULT_MAX_CONCURRENT,
                0,
                self._logger,
            )
            self._guards[method] = guard
        return guard

    async def intercept_unary_unary(
        self,
        continuation: Callable[..., Awaitable[Any]],
        client_call_details: grpc_aio.ClientCallDetails,
        request: Any,
    ) -> Any:
        method = client_call_details.method.decode()
        guard = self._guard_for(method)

        details = client_call_details
        if _DEFAULT_CALL_TIMEOUT > 0:
            existing = details.timeout
            effective = (
                min(existing, _DEFAULT_CALL_TIMEOUT)
                if existing is not None
                else _DEFAULT_CALL_TIMEOUT
            )
            details = details._replace(timeout=effective)

        async def invoke() -> Any:
            call = await continuation(details, request)
            return await call

        try:
            return await guard.call(invoke)
        except DependencyGuardOpenError:
            raise grpc.aio.AioRpcError(
                grpc.StatusCode.UNAVAILABLE,
                details=(
                    f'dependency "{method}" is temporarily unavailable '
                    "(circuit breaker open)"
                ),
            ) from None
        except DependencyGuardBulkheadError:
            raise grpc.aio.AioRpcError(
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                details=f'dependency "{method}" has too many concurrent requests',
            ) from None
