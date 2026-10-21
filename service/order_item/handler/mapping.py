"""Row -> proto message mapping for the order item handlers. dispatches on the concrete row type in one `mapToProtoOrderItemResponse` switch; Python reads the shared attribute names directly, since every projection reuses one field set per message shape. Timestamps use the millisecond layout `%Y-%m-%d %H:%M:%S.mmm` (same as banner — do not unify with category's `%Y-%m-%d`). Unlike category, `deleted_at` is attached **only when non-empty**: guards with `if val:= formatTimestamp(deletedAt); val != ""`, so a NULL timestamp leaves the wrapper unset."""

from __future__ import annotations

from typing import Any

from google.protobuf import wrappers_pb2

from shared.convert.convert import format_timestamp_millis


def fill_order_item_response(message: Any, row: Any) -> None:
    """Fill an `OrderItemResponse` (create/update/read projections)."""
    message.id = int(row.order_item_id)
    message.order_id = int(row.order_id)
    message.product_id = int(row.product_id)
    message.quantity = int(row.quantity)
    message.price = int(row.price)
    message.created_at = format_timestamp_millis(row.created_at)
    message.updated_at = format_timestamp_millis(row.updated_at)


def fill_order_item_response_delete_at(message: Any, row: Any) -> None:
    """Fill an `OrderItemResponseDeleteAt` (trash/restore/active projections)."""
    fill_order_item_response(message, row)
    deleted_at = format_timestamp_millis(row.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


__all__ = ["fill_order_item_response", "fill_order_item_response_delete_at"]
