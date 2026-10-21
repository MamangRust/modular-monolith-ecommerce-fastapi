from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsByOrderRow,
    OrderItem,
    UpdateOrderItemRow,
)
from pkg.resilience.dependency_guard import DependencyGuard
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.errors import (
    err_calculate_total_price,
    err_create_order_item,
    err_delete_order_item_permanent,
    err_find_order_item_by_order,
    err_restore_all_order_item,
    err_restore_order_item,
    err_trashed_order_item,
    err_update_order_item,
)
from shared.errors.order_item_errors import (
    err_delete_all_order_permanent as err_delete_all_order_item_permanent,
)

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


def _parse_deleted_at(pb: Any) -> datetime | None:
    return _parse_time(pb.deleted_at.value) if pb.HasField("deleted_at") else None


class OrderItemQueryAdapter:

    def __init__(
        self,
        query_channel: grpc_aio.Channel,
        command_channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        row_cls: Any = None,
    ) -> None:
        from pb.order_item import (
            order_item_command_pb2,
            order_item_command_pb2_grpc,
            order_item_common_pb2,
            order_item_query_pb2_grpc,
        )

        self._common = order_item_common_pb2
        self._command_pb2 = order_item_command_pb2
        self._query = order_item_query_pb2_grpc.OrderItemQueryServiceStub(
            query_channel
        )
        self._command = order_item_command_pb2_grpc.OrderItemCommandServiceStub(
            command_channel
        )
        self._guard = guard
        self._row_cls: Any = row_cls or GetOrderItemsByOrderRow

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_order_item_by_order(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow]:
        async def invoke() -> Any:
            return await self._query.FindOrderItemByOrder(
                self._common.FindByIdOrderItemRequest(id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_find_order_item_by_order.with_internal(exc) from exc

        return [
            self._row_cls(
                order_item_id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                created_at=_parse_time(item.created_at),
                updated_at=_parse_time(item.updated_at),
            )
            for item in resp.data
        ]

    async def calculate_total_price(self, order_id: int) -> int:
        async def invoke() -> Any:
            return await self._command.CalculateTotalPrice(
                self._command_pb2.CalculateTotalPriceRequest(order_id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_calculate_total_price.with_internal(exc) from exc

        return int(resp.total_price)


class OrderItemCommandAdapter:

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        create_row_cls: Any = None,
        order_item_cls: Any = None,
    ) -> None:
        from pb.order_item import (
            order_item_command_pb2,
            order_item_command_pb2_grpc,
            order_item_common_pb2,
        )

        self._common = order_item_common_pb2
        self._pb2 = order_item_command_pb2
        self._command = order_item_command_pb2_grpc.OrderItemCommandServiceStub(
            channel
        )
        self._guard = guard
        self._create_row_cls: Any = create_row_cls or CreateOrderItemRow
        self._order_item_cls: Any = order_item_cls or OrderItem

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def create(
        self, request: CreateOrderItemRecordRequest
    ) -> CreateOrderItemRow:
        async def invoke() -> Any:
            return await self._command.CreateOrderItem(
                self._pb2.CreateOrderItemRecordRequest(
                    order_id=request.order_id,
                    product_id=request.product_id,
                    quantity=request.quantity,
                    price=request.price,
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_create_order_item.with_internal(exc) from exc

        data = resp.data
        return self._create_row_cls(
            order_item_id=data.id,
            order_id=data.order_id,
            product_id=data.product_id,
            quantity=data.quantity,
            price=data.price,
            created_at=_parse_time(data.created_at),
            updated_at=_parse_time(data.updated_at),
        )

    async def update(
        self, request: UpdateOrderItemRecordRequest
    ) -> UpdateOrderItemRow:
        async def invoke() -> Any:
            return await self._command.UpdateOrderItem(
                self._pb2.UpdateOrderItemRecordRequest(
                    order_item_id=request.order_item_id,
                    quantity=request.quantity,
                    price=request.price,
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_update_order_item.with_internal(exc) from exc

        data = resp.data
        return self._create_row_cls(
            order_item_id=data.id,
            order_id=data.order_id,
            product_id=data.product_id,
            quantity=data.quantity,
            price=data.price,
            created_at=_parse_time(data.created_at),
            updated_at=_parse_time(data.updated_at),
        )

    async def trash(self, order_item_id: int) -> OrderItem:
        async def invoke() -> Any:
            return await self._command.TrashOrderItem(
                self._common.FindByIdOrderItemRequest(id=order_item_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_trashed_order_item.with_internal(exc) from exc

        return self._row_from_delete_at(resp.data)

    async def restore(self, order_item_id: int) -> OrderItem:
        async def invoke() -> Any:
            return await self._command.RestoreOrderItem(
                self._common.FindByIdOrderItemRequest(id=order_item_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_restore_order_item.with_internal(exc) from exc

        return self._row_from_delete_at(resp.data)

    async def delete_permanent(self, order_item_id: int) -> bool:
        async def invoke() -> Any:
            return await self._command.DeleteOrderItemPermanent(
                self._common.FindByIdOrderItemRequest(id=order_item_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_delete_order_item_permanent.with_internal(exc) from exc

        return resp.status == "success"

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        async def invoke() -> Any:
            return await self._command.DeleteOrderItemByOrderPermanent(
                self._common.FindByIdOrderItemRequest(id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_delete_order_item_permanent.with_internal(exc) from exc

        return resp.status == "success"

    async def restore_all(self) -> bool:
        from google.protobuf.empty_pb2 import Empty

        async def invoke() -> Any:
            return await self._command.RestoreAllOrdersItem(
                Empty(), timeout=_TIMEOUT_SECONDS
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_restore_all_order_item.with_internal(exc) from exc

        return resp.status == "success"

    async def delete_all(self) -> bool:
        from google.protobuf.empty_pb2 import Empty

        async def invoke() -> Any:
            return await self._command.DeleteAllPermanentOrdersItem(
                Empty(), timeout=_TIMEOUT_SECONDS
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_delete_all_order_item_permanent.with_internal(exc) from exc

        return resp.status == "success"

    def _row_from_delete_at(self, pb: Any) -> OrderItem:
        return self._order_item_cls(
            order_item_id=pb.id,
            order_id=pb.order_id,
            product_id=pb.product_id,
            quantity=pb.quantity,
            price=pb.price,
            created_at=_parse_time(pb.created_at),
            updated_at=_parse_time(pb.updated_at),
            deleted_at=_parse_deleted_at(pb),
        )


__all__ = ["OrderItemCommandAdapter", "OrderItemQueryAdapter"]
