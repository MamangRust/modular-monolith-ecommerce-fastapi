"""Row -> proto message mapping for the shipping address handlers. dispatches on the concrete row type in one `mapToProtoShippingResponse` switch; Python reads the shared attribute names directly, since every projection reuses one field set per message shape. Timestamps use the **date-only** layout `%Y-%m-%d` (same as category — not the millisecond layout used by banner/order_item). `shipping_cost` is a `float` on the row and is truncated to `int32` on the wire (`int(row.shipping_cost)`). `deleted_at` is attached **only when non-empty**: guards with `if s.DeletedAt.Valid`, so a NULL timestamp leaves the wrapper unset."""

from __future__ import annotations

from typing import Any

from google.protobuf import wrappers_pb2

from shared.convert.convert import format_date


def fill_shipping_response(message: Any, row: Any) -> None:
    """Fill a `ShippingResponse` (create/update/read projections)."""
    message.id = int(row.shipping_address_id)
    message.order_id = int(row.order_id)
    message.alamat = row.alamat
    message.provinsi = row.provinsi
    message.negara = row.negara
    message.kota = row.kota
    message.shippingMethod = row.shipping_method
    message.shippingCost = int(row.shipping_cost)
    message.created_at = format_date(row.created_at)
    message.updated_at = format_date(row.updated_at)
    message.courier = row.courier


def fill_shipping_response_delete_at(message: Any, row: Any) -> None:
    """Fill a `ShippingResponseDeleteAt` (trash/restore/active projections)."""
    fill_shipping_response(message, row)
    deleted_at = format_date(row.deleted_at)
    if deleted_at:
        message.deleted_at.CopyFrom(wrappers_pb2.StringValue(value=deleted_at))


__all__ = ["fill_shipping_response", "fill_shipping_response_delete_at"]
