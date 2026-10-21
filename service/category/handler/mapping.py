"""Row -> proto message mapping for the category handlers. dispatches on the concrete row type in one `mapToCategoryResponse` switch; Python reads the shared attribute names directly, since the projections reuse one field set per message shape (the by-id / by-merchant rows alias the base stats rows). Timestamps are formatted `%Y-%m-%d` (category's layout — do not unify with banner's millisecond layout). dereferences the nullable `description`/`slug_category`/`image_category` pointers directly; renders NULL as `""` (see Planning.md). `deleted_at` is always attached as a `StringValue` wrapper (sets the pointer unconditionally), so a NULL timestamp renders as `""`."""

from __future__ import annotations

from typing import Any

from google.protobuf import wrappers_pb2

from shared.convert.convert import format_date


def fill_category_response(message: Any, row: Any) -> None:
    """Fill a `CategoryResponse` (active / created / updated projections)."""
    message.id = int(row.category_id)
    message.name = row.name
    message.description = row.description or ""
    message.slug_category = row.slug_category or ""
    message.image_category = row.image_category or ""
    message.created_at = format_date(row.created_at)
    message.updated_at = format_date(row.updated_at)


def fill_category_response_delete_at(message: Any, row: Any) -> None:
    """Fill a `CategoryResponseDeleteAt` (trash/restore/active projections)."""
    fill_category_response(message, row)
    # always sets the pointer ("" for an invalid/NULL timestamp).
    message.deleted_at.CopyFrom(
        wrappers_pb2.StringValue(value=format_date(row.deleted_at))
    )


def fill_monthly_total_price(message: Any, row: Any) -> None:
    message.year = row.year
    message.month = row.month
    message.total_revenue = int(row.total_revenue)


def fill_yearly_total_price(message: Any, row: Any) -> None:
    message.year = row.year
    message.total_revenue = int(row.total_revenue)


def fill_month_price(message: Any, row: Any) -> None:
    message.month = row.month
    message.category_id = int(row.category_id)
    message.category_name = row.category_name
    message.order_count = int(row.order_count)
    message.items_sold = int(row.items_sold)
    message.total_revenue = int(row.total_revenue)


def fill_year_price(message: Any, row: Any) -> None:
    message.year = row.year
    message.category_id = int(row.category_id)
    message.category_name = row.category_name
    message.order_count = int(row.order_count)
    message.items_sold = int(row.items_sold)
    message.total_revenue = int(row.total_revenue)
    message.unique_products_sold = int(row.unique_products_sold)


__all__ = [
    "fill_category_response",
    "fill_category_response_delete_at",
    "fill_month_price",
    "fill_monthly_total_price",
    "fill_year_price",
    "fill_yearly_total_price",
]
