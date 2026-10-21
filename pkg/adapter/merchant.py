from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.merchant import GetMerchantByIDRow
from pkg.resilience.dependency_guard import DependencyGuard
from shared.errors import err_merchant_internal

_TIMEOUT_SECONDS = 30
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def _parse_time(value: str) -> datetime:
    """Parse a `%Y-%m-%d %H:%M:%S` proto timestamp; epoch when absent."""
    if not value:
        return _EPOCH
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return _EPOCH
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


class MerchantQueryAdapter:

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        row_cls: Any = None,
    ) -> None:
        from pb.merchant import merchant_common_pb2, merchant_query_pb2_grpc

        self._pb2 = merchant_common_pb2  # FindByIdMerchantRequest lives here
        self._query = merchant_query_pb2_grpc.MerchantQueryServiceStub(channel)
        self._guard = guard
        self._row_cls: Any = row_cls or GetMerchantByIDRow

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_by_id(self, merchant_id: int) -> Any:
        async def invoke() -> Any:
            return await self._query.FindById(
                self._pb2.FindByIdMerchantRequest(id=merchant_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_merchant_internal.with_internal(exc) from exc

        data = resp.data
        return self._row_cls(
            merchant_id=data.id,
            user_id=data.user_id,
            name=data.name,
            description=data.description,
            address=data.address,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            status=data.status,
            created_at=_parse_time(data.created_at),
            updated_at=_parse_time(data.updated_at),
        )


__all__ = ["MerchantQueryAdapter"]
