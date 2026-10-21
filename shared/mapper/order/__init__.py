"""Order REST mappers."""

from __future__ import annotations

from shared.mapper.order.command import (
    to_api_response_order,
    to_api_response_order_all,
    to_api_response_order_delete,
    to_api_response_order_delete_at,
    to_response_order,
    to_response_order_delete_at,
    to_responses_order,
    to_responses_order_delete_at,
)
from shared.mapper.order.mapper import (
    map_order_monthly_response,
    map_order_monthly_total_revenue_response,
    map_order_response,
    map_order_response_delete_at,
    map_order_yearly_response,
    map_order_yearly_total_revenue_response,
    map_pagination_meta,
)
from shared.mapper.order.query import (
    to_api_response_pagination_order,
    to_api_response_pagination_order_delete_at,
    to_api_responses_orders,
)
from shared.mapper.order.stats import (
    to_api_response_monthly_order,
    to_api_response_monthly_total_revenue,
    to_api_response_yearly_order,
    to_api_response_yearly_total_revenue,
    to_order_monthly_price,
    to_order_monthly_prices,
    to_order_yearly_price,
    to_order_yearly_prices,
    to_response_order_monthly_total_revenue,
    to_response_order_monthly_total_revenues,
    to_response_order_yearly_total_revenue,
    to_response_order_yearly_total_revenues,
)

__all__ = [
    "map_order_monthly_response",
    "map_order_monthly_total_revenue_response",
    "map_order_response",
    "map_order_response_delete_at",
    "map_order_yearly_response",
    "map_order_yearly_total_revenue_response",
    "map_pagination_meta",
    "to_api_response_monthly_order",
    "to_api_response_monthly_total_revenue",
    "to_api_response_order",
    "to_api_response_order_all",
    "to_api_response_order_delete",
    "to_api_response_order_delete_at",
    "to_api_response_pagination_order",
    "to_api_response_pagination_order_delete_at",
    "to_api_responses_orders",
    "to_api_response_yearly_order",
    "to_api_response_yearly_total_revenue",
    "to_order_monthly_price",
    "to_order_monthly_prices",
    "to_order_yearly_price",
    "to_order_yearly_prices",
    "to_response_order",
    "to_response_order_delete_at",
    "to_response_order_monthly_total_revenue",
    "to_response_order_monthly_total_revenues",
    "to_response_order_yearly_total_revenue",
    "to_response_order_yearly_total_revenues",
    "to_responses_order",
    "to_responses_order_delete_at",
]
