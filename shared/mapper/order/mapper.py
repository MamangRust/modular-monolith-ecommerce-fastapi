"""Order proto -> response DTO mapping. The proto already carries formatted timestamp strings, so this layer only shapes them into the REST envelopes. `OrderResponseDeleteAt.deleted_at` is always emitted: command mapper sets the pointer unconditionally (`""` when the proto `StringValue` wrapper is absent), so passes `""` rather than `None` in that case."""

from __future__ import annotations

from typing import Any

from shared.domain.response.order import (
    OrderMonthlyResponse,
    OrderMonthlyTotalRevenueResponse,
    OrderResponse,
    OrderResponseDeleteAt,
    OrderYearlyResponse,
    OrderYearlyTotalRevenueResponse,
)
from shared.domain.response.responses import PaginationMeta


def map_order_response(pb: Any) -> OrderResponse:
    return OrderResponse(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        user_id=int(pb.user_id),
        total_price=int(pb.total_price),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
    )


def map_order_response_delete_at(pb: Any) -> OrderResponseDeleteAt:
    deleted_at = pb.deleted_at.value if pb.HasField("deleted_at") else ""
    return OrderResponseDeleteAt(
        id=int(pb.id),
        merchant_id=int(pb.merchant_id),
        user_id=int(pb.user_id),
        total_price=int(pb.total_price),
        created_at=pb.created_at,
        updated_at=pb.updated_at,
        deleted_at=deleted_at,
    )


def map_order_monthly_response(pb: Any) -> OrderMonthlyResponse:
    return OrderMonthlyResponse(
        month=pb.month,
        order_count=int(pb.order_count),
        total_revenue=int(pb.total_revenue),
        total_items_sold=int(pb.total_items_sold),
    )


def map_order_yearly_response(pb: Any) -> OrderYearlyResponse:
    return OrderYearlyResponse(
        year=pb.year,
        order_count=int(pb.order_count),
        total_revenue=int(pb.total_revenue),
        total_items_sold=int(pb.total_items_sold),
        active_cashiers=int(pb.active_cashiers),
        unique_products_sold=int(pb.unique_products_sold),
    )


def map_order_monthly_total_revenue_response(
    pb: Any,
) -> OrderMonthlyTotalRevenueResponse:
    return OrderMonthlyTotalRevenueResponse(
        year=pb.year,
        month=pb.month,
        order_count=int(pb.order_count),
        total_revenue=int(pb.total_revenue),
        total_items_sold=int(pb.total_items_sold),
    )


def map_order_yearly_total_revenue_response(
    pb: Any,
) -> OrderYearlyTotalRevenueResponse:
    return OrderYearlyTotalRevenueResponse(
        year=pb.year,
        order_count=int(pb.order_count),
        total_revenue=int(pb.total_revenue),
    )


def map_pagination_meta(meta: Any) -> PaginationMeta:
    if meta is None:
        return PaginationMeta()
    return PaginationMeta(
        current_page=int(meta.current_page),
        page_size=int(meta.page_size),
        total_pages=int(meta.total_pages),
        total_records=int(meta.total_records),
    )


__all__ = [
    "map_order_monthly_response",
    "map_order_monthly_total_revenue_response",
    "map_order_response",
    "map_order_response_delete_at",
    "map_order_yearly_response",
    "map_order_yearly_total_revenue_response",
    "map_pagination_meta",
]
