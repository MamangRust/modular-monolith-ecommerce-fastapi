"""Unit tests for pkg.resilience.client_interceptor (gateway per-method
guards): deadline shrinking, breaker opening mapped to UNAVAILABLE, and
bulkhead rejection mapped to RESOURCE_EXHAUSTED."""

import grpc
import grpc.aio as grpc_aio
import pytest

from pkg.logger.logger import Logger
from pkg.resilience.client_interceptor import (
    _DEFAULT_CALL_TIMEOUT,
    DependencyGuardInterceptor,
)
from pkg.resilience.dependency_guard import DependencyGuardOpenError

_METHOD = b"/pb.auth.AuthService/Hello"


def _details(timeout: float | None) -> grpc_aio.ClientCallDetails:
    return grpc_aio.ClientCallDetails(
        method=_METHOD,
        timeout=timeout,
        metadata=None,
        credentials=None,
        wait_for_ready=None,
    )


def _interceptor() -> DependencyGuardInterceptor:
    return DependencyGuardInterceptor(Logger("test", "error"))


async def test_deadline_shrunk_to_guard_timeout() -> None:
    interceptor = _interceptor()
    seen: dict[str, object] = {}

    async def continuation(details, request):
        seen["timeout"] = details.timeout

        class FakeCall:
            def __await__(self):
                if False:
                    yield
                return "resp"

        return FakeCall()

    result = await interceptor.intercept_unary_unary(continuation, _details(30.0), "req")
    assert result == "resp"
    assert seen["timeout"] == _DEFAULT_CALL_TIMEOUT


async def test_deadline_kept_when_already_shorter() -> None:
    interceptor = _interceptor()
    seen: dict[str, object] = {}

    async def continuation(details, request):
        seen["timeout"] = details.timeout

        class FakeCall:
            def __await__(self):
                if False:
                    yield
                return "resp"

        return FakeCall()

    await interceptor.intercept_unary_unary(continuation, _details(0.5), "req")
    assert seen["timeout"] == 0.5


async def test_guards_are_keyed_per_method() -> None:
    interceptor = _interceptor()
    a = interceptor._guard_for("/pkg.A/Get")
    b = interceptor._guard_for("/pkg.B/Get")
    assert a is not b
    assert interceptor._guard_for("/pkg.A/Get") is a


async def test_open_breaker_maps_to_unavailable() -> None:
    interceptor = _interceptor()
    guard = interceptor._guard_for(_METHOD.decode())
    for _ in range(5):
        guard._breaker.record_failure()

    async def continuation(details, request):
        raise AssertionError("must not be invoked when the breaker is open")

    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await interceptor.intercept_unary_unary(continuation, _details(30.0), "req")
    assert exc.value.code() == grpc.StatusCode.UNAVAILABLE


async def test_bulkhead_rejection_maps_to_resource_exhausted() -> None:
    interceptor = _interceptor()
    guard = interceptor._guard_for(_METHOD.decode())
    while guard._limiter.try_acquire():
        pass

    async def continuation(details, request):
        raise AssertionError("must not be invoked when the bulkhead is full")

    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await interceptor.intercept_unary_unary(continuation, _details(30.0), "req")
    assert exc.value.code() == grpc.StatusCode.RESOURCE_EXHAUSTED


async def test_rejection_does_not_touch_the_breaker_state() -> None:
    interceptor = _interceptor()
    guard = interceptor._guard_for(_METHOD.decode())
    for _ in range(5):
        guard._breaker.record_failure()
    failures_before = guard._breaker.get_failure_count()

    async def call() -> None:
        raise AssertionError("unreachable")

    with pytest.raises(DependencyGuardOpenError):
        await guard.call(call)

    # A guard rejection is not a dependency observation: the failure count
    # must stay where the recorded failures left it.
    assert guard._breaker.get_failure_count() == failures_before
