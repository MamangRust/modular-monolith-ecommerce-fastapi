"""Order response DTOs. Field names match the REST DTOs. Timestamp strings are already formatted by the gRPC handlers (`%Y-%m-%d %H:%M:%S.mmm`) and passed through unchanged. `OrderResponseDeleteAt.deleted_at` is a nullable string: the mapper sets it whenever the proto wrapper is present (mapper always sets the pointer, so the REST key is always emitted — `""` when absent). The stats envelopes carry **no** pagination block (declares none), and the handler leaves `active_cashiers` / `order_count` / `total_items_sold` at their zero values where does (see the handler mapping)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.domain.response.responses import (
    ApiResponse,
    APIResponsePagination,
)


@dataclass
class OrderResponse:
    id: int
    merchant_id: int
    user_id: int
    total_price: int
    created_at: str
    updated_at: str


@dataclass
class OrderResponseDeleteAt:
    id: int
    merchant_id: int
    user_id: int
    total_price: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


@dataclass
class OrderMonthlyResponse:
    month: str
    order_count: int
    total_revenue: int
    total_items_sold: int


@dataclass
class OrderYearlyResponse:
    year: str
    order_count: int
    total_revenue: int
    total_items_sold: int
    active_cashiers: int
    unique_products_sold: int


@dataclass
class OrderMonthlyTotalRevenueResponse:
    year: str
    month: str
    order_count: int
    total_revenue: int
    total_items_sold: int


@dataclass
class OrderYearlyTotalRevenueResponse:
    year: str
    order_count: int
    total_revenue: int


# API response wrappers (kept close to the names) ----

OrderResponseApi = ApiResponse[OrderResponse]
OrderResponseDeleteAtApi = ApiResponse[OrderResponseDeleteAt]
OrderResponses = ApiResponse[list[OrderResponse]]
OrderResponseDelete = ApiResponse[None]
OrderResponseAll = ApiResponse[None]
OrderResponsePagination = APIResponsePagination[list[OrderResponse]]
OrderResponsePaginationDeleteAt = APIResponsePagination[list[OrderResponseDeleteAt]]
OrderMonthlyApi = ApiResponse[list[OrderMonthlyResponse]]
OrderYearlyApi = ApiResponse[list[OrderYearlyResponse]]
OrderMonthlyTotalRevenueApi = ApiResponse[list[OrderMonthlyTotalRevenueResponse]]
OrderYearlyTotalRevenueApi = ApiResponse[list[OrderYearlyTotalRevenueResponse]]


def to_api_response_order_delete(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


def to_api_response_order_all(pb: Any) -> ApiResponse[None]:
    return ApiResponse[None](status=pb.status, message=pb.message, data=None)


__all__ = [
    "OrderMonthlyApi",
    "OrderMonthlyResponse",
    "OrderMonthlyTotalRevenueApi",
    "OrderMonthlyTotalRevenueResponse",
    "OrderResponse",
    "OrderResponseAll",
    "OrderResponseApi",
    "OrderResponseDelete",
    "OrderResponseDeleteAt",
    "OrderResponseDeleteAtApi",
    "OrderResponsePagination",
    "OrderResponsePaginationDeleteAt",
    "OrderResponses",
    "OrderYearlyApi",
    "OrderYearlyResponse",
    "OrderYearlyTotalRevenueApi",
    "OrderYearlyTotalRevenueResponse",
    "to_api_response_order_all",
    "to_api_response_order_delete",
]
