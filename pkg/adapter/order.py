from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.order import Order
from pkg.resilience.dependency_guard import DependencyGuard
from shared.errors.order_errors import err_find_by_id

_TIMEOUT_SECONDS = 30
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def _parse_time(value: str) -> datetime:
    """Parse a `%Y-%m-%d %H:%M:%S.mmm` proto timestamp; epoch when absent."""
    if not value:
        return _EPOCH
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return _EPOCH
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


class OrderQueryAdapter:

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        order_cls: Any = None,
    ) -> None:
        from pb.order import order_common_pb2, order_query_pb2_grpc

        self._common = order_common_pb2
        self._query = order_query_pb2_grpc.OrderQueryServiceStub(channel)
        self._guard = guard
        self._order_cls: Any = order_cls or Order

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_by_id(self, order_id: int) -> Order:
        async def invoke() -> Any:
            return await self._query.FindById(
                self._common.FindByIdOrderRequest(id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_find_by_id.with_internal(exc) from exc

        data = getattr(resp, "data", None)
        if data is None:
            raise err_find_by_id

        return self._order_cls(
            order_id=data.id,
            user_id=data.user_id,
            merchant_id=data.merchant_id,
            total_price=int(data.total_price),
            created_at=_parse_time(data.created_at),
            updated_at=_parse_time(data.updated_at),
        )


__all__ = ["OrderQueryAdapter"]
