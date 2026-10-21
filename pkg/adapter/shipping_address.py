"""Shipping-address gRPC adapters. The order service creates/updates shipping addresses remotely through the command adapter and reads them back through the query adapter, instead of touching the `shipping_addresses` table. command adapter checks `errors.Is(err, pgx.ErrNoRows)` before choosing `ErrShippingAddressNotFound` vs the per-verb error; a remote gRPC error can never match the local pgx sentinel, so the reachable branch is always the per-verb error —. holds the query client raw and does **not** wrap its errors; (errors propagate untouched). `FindById`/`FindByOrder` return the proto `ShippingResponse` (or `None` when the envelope carries no `data`, `shippingRes.Data == nil` guard, which the service checks). deliberately wires both (documented fix; see Planning.md). The command adapter's row carries `created_at`/`updated_at`, which leaves at their `pgtype.Timestamp` zero value (the order service never reads them). parses the proto's date-only `%Y-%m-%d` strings into datetimes so the rows stay well-typed, falling back to the epoch when absent — the same normalisation as the order-item adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    UpdateShippingAddressRow,
)
from pkg.resilience.dependency_guard import DependencyGuard
from shared.convert.convert import DATE_FMT
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors import (
    err_create_shipping_address,
    err_delete_all_permanent_shipping_address,
    err_delete_shipping_address_permanent,
    err_update_shipping_address,
)

_TIMEOUT_SECONDS = 30
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def _parse_date(value: str) -> datetime:
    """Parse a `%Y-%m-%d` proto timestamp; epoch when absent."""
    if not value:
        return _EPOCH
    try:
        parsed = datetime.strptime(value, DATE_FMT)
    except ValueError:
        return _EPOCH
    return parsed.replace(tzinfo=UTC)


class ShippingCommandAdapter:

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        row_cls: Any = None,
    ) -> None:
        from pb.shipping_address import (
            shipping_address_command_pb2,
            shipping_address_command_pb2_grpc,
            shipping_address_common_pb2,
        )

        self._common = shipping_address_common_pb2
        self._pb2 = shipping_address_command_pb2
        self._command = (
            shipping_address_command_pb2_grpc.ShippingCommandServiceStub(channel)
        )
        self._guard = guard
        self._row_cls: Any = row_cls or CreateShippingAddressRow

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def create(
        self, request: CreateShippingAddressRequest
    ) -> CreateShippingAddressRow:
        async def invoke() -> Any:
            return await self._command.CreateShipping(
                self._pb2.CreateShippingAddressRequest(
                    order_id=request.order_id,
                    alamat=request.alamat,
                    provinsi=request.provinsi,
                    kota=request.kota,
                    courier=request.courier,
                    shipping_method=request.shipping_method,
                    shipping_cost=request.shipping_cost,
                    negara=request.negara,
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_create_shipping_address.with_internal(exc) from exc

        return self._row_from(resp.data)

    async def update(
        self, request: UpdateShippingAddressRequest
    ) -> UpdateShippingAddressRow:
        async def invoke() -> Any:
            return await self._command.UpdateShipping(
                self._pb2.UpdateShippingAddressRequest(
                    shipping_id=request.shipping_id,
                    alamat=request.alamat,
                    provinsi=request.provinsi,
                    kota=request.kota,
                    courier=request.courier,
                    shipping_method=request.shipping_method,
                    shipping_cost=request.shipping_cost,
                    negara=request.negara,
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_update_shipping_address.with_internal(exc) from exc

        return self._row_from(resp.data)

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        async def invoke() -> Any:
            return await self._command.DeleteShippingByOrderPermanent(
                self._common.FindByIdShippingRequest(id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_delete_shipping_address_permanent.with_internal(exc) from exc

        return True

    async def delete_all(self) -> bool:
        from google.protobuf.empty_pb2 import Empty

        async def invoke() -> Any:
            return await self._command.DeleteAllShippingPermanent(
                Empty(), timeout=_TIMEOUT_SECONDS
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_delete_all_permanent_shipping_address.with_internal(exc) from exc

        return resp.status == "success"

    def _row_from(self, pb: Any) -> Any:
        return self._row_cls(
            shipping_address_id=pb.id,
            order_id=pb.order_id,
            alamat=pb.alamat,
            provinsi=pb.provinsi,
            negara=pb.negara,
            kota=pb.kota,
            courier=pb.courier,
            shipping_method=pb.shippingMethod,
            shipping_cost=float(pb.shippingCost),
            created_at=_parse_date(pb.created_at),
            updated_at=_parse_date(pb.updated_at),
        )


class ShippingQueryAdapter:
    """ShippingQueryServiceClient` usage. Returns the proto `ShippingResponse` (or `None` when the envelope has no `data`); errors propagate untouched,."""

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
    ) -> None:
        from pb.shipping_address import (
            shipping_address_common_pb2,
            shipping_address_query_pb2_grpc,
        )

        self._common = shipping_address_common_pb2
        self._query = shipping_address_query_pb2_grpc.ShippingQueryServiceStub(
            channel
        )
        self._guard = guard

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_by_id(self, shipping_id: int) -> Any:
        async def invoke() -> Any:
            return await self._query.FindById(
                self._common.FindByIdShippingRequest(id=shipping_id),
                timeout=_TIMEOUT_SECONDS,
            )

        resp = await guard_call(self._guard, invoke)
        return resp.data if resp.HasField("data") else None

    async def find_by_order(self, order_id: int) -> Any:
        async def invoke() -> Any:
            return await self._query.FindByOrder(
                self._common.FindByIdShippingRequest(id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        resp = await guard_call(self._guard, invoke)
        return resp.data if resp.HasField("data") else None


__all__ = ["ShippingCommandAdapter", "ShippingQueryAdapter"]
