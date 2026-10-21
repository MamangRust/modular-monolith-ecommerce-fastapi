"""Order item row/proto -> response DTO mapping. Two input shapes, one output: - row dataclasses — format the timestamps the way the handlers do (`%Y-%m-%d %H:%M:%S.mmm`); - proto messages — already-formatted strings, passed through unchanged. The `...DeleteAt` shape always carries `deleted_at` (stores a pointer to a possibly-empty string); the proto only sets the wrapper when non-empty, so an absent wrapper renders as `""`."""

from __future__ import annotations

from typing import Any

from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    OrderItem,
    UpdateOrderItemRow,
)
from shared.convert.convert import format_timestamp_millis
from shared.domain.response.order_item import (
    OrderItemResponse,
    OrderItemResponseDeleteAt,
)

OrderItemRow = (
    OrderItem
    | CreateOrderItemRow
    | UpdateOrderItemRow
    | GetOrderItemsRow
    | GetOrderItemsByOrderRow
)
OrderItemDeleteAtRow = OrderItem | GetOrderItemsActiveRow


def to_order_item_response(row: OrderItemRow) -> OrderItemResponse:
    return OrderItemResponse(
        id=row.order_item_id,
        order_id=row.order_id,
        product_id=row.product_id,
        quantity=row.quantity,
        price=row.price,
        created_at=format_timestamp_millis(row.created_at),
        updated_at=format_timestamp_millis(row.updated_at),
    )


def to_order_item_response_delete_at(
    row: OrderItemDeleteAtRow,
) -> OrderItemResponseDeleteAt:
    return OrderItemResponseDeleteAt(
        id=row.order_item_id,
        order_id=row.order_id,
        product_id=row.product_id,
        quantity=row.quantity,
        price=row.price,
        created_at=format_timestamp_millis(row.created_at),
        updated_at=format_timestamp_millis(row.updated_at),
        deleted_at=format_timestamp_millis(row.deleted_at),
    )


def map_order_item_response(pb: Any) -> OrderItemResponse:
    return OrderItemResponse(
        id=int(pb.id),
        order_id=int(pb.order_id),
        product_id=int(pb.product_id),
        quantity=int(pb.quantity),
        price=int(pb.price),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_order_item_response_delete_at(pb: Any) -> OrderItemResponseDeleteAt:
    # always sets the pointer, so an absent wrapper renders as "".
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return OrderItemResponseDeleteAt(
        id=int(pb.id),
        order_id=int(pb.order_id),
        product_id=int(pb.product_id),
        quantity=int(pb.quantity),
        price=int(pb.price),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


__all__ = [
    "OrderItemDeleteAtRow",
    "OrderItemRow",
    "map_order_item_response",
    "map_order_item_response_delete_at",
    "to_order_item_response",
    "to_order_item_response_delete_at",
]
