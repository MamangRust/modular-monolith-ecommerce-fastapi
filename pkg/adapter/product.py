"""Product gRPC adapters. Consumers that must resolve a product remotely (cart, review, order) call the product service through these adapters instead of touching the products table. Maps proto `ProductResponse` onto the product service's own row shapes. `ProductQueryAdapter` (also reused by review/order): cart adapter wraps *any* error as `product_errors.ErrProductNotFound` (404 "product not found") — a 500 from the product service also becomes 404. It also dereferences `res.Data` directly (no presence check), so a missing envelope yields zero values. `ProductCommandAdapter`: it exposes the two stock-mutating RPCs (`UpdateProductCountStock`, `AdjustProductStock`). checks `errors.Is(err, pgx.ErrNoRows)` before choosing `ErrProductNotFound` vs `ErrProductInternal`, but a remote gRPC error can never match the local pgx sentinel, so the reachable branch is always `ErrProductInternal` — and wraps every failure as `err_product_internal`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.product import AdjustProductStockRow, GetProductByIDRow
from pkg.resilience.dependency_guard import DependencyGuard
from shared.errors import err_product_internal, err_product_not_found

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


class ProductQueryAdapter:

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        row_cls: Any = None,
    ) -> None:
        from pb.product import product_common_pb2, product_query_pb2_grpc

        self._pb2 = product_common_pb2  # FindByIdProductRequest lives here
        self._query = product_query_pb2_grpc.ProductQueryServiceStub(channel)
        self._guard = guard
        self._row_cls: Any = row_cls or GetProductByIDRow

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_by_id(self, product_id: int) -> Any:
        async def invoke() -> Any:
            return await self._query.FindById(
                self._pb2.FindByIdProductRequest(id=product_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_product_not_found.with_internal(exc) from exc

        data = resp.data
        return self._row_cls(
            product_id=data.id,
            merchant_id=data.merchant_id,
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            price=data.price,
            count_in_stock=data.count_in_stock,
            brand=data.brand,
            weight=data.weight,
            rating=data.rating,
            slug_product=data.slug_product,
            image_product=data.image_product,
            created_at=_parse_time(data.created_at),
            updated_at=_parse_time(data.updated_at),
        )


class ProductCommandAdapter:
    """Both RPCs return the mutated product (id + new count) and every remote failure is wrapped as `err_product_internal` (see the module docstring for why the `pgx.ErrNoRows` branch is unreachable)."""

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        row_cls: Any = None,
    ) -> None:
        from pb.product import product_command_pb2, product_command_pb2_grpc

        self._pb2 = product_command_pb2
        self._command = product_command_pb2_grpc.ProductCommandServiceStub(channel)
        self._guard = guard
        self._row_cls: Any = row_cls or AdjustProductStockRow

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def update_product_count_stock(
        self, product_id: int, stock: int
    ) -> Any:
        async def invoke() -> Any:
            return await self._command.UpdateProductCountStock(
                self._pb2.UpdateProductCountStockRequest(
                    product_id=product_id, stock=stock
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_product_internal.with_internal(exc) from exc

        data = resp.data
        return self._row_cls(
            product_id=data.id,
            count_in_stock=data.count_in_stock,
        )

    async def adjust_product_stock(
        self, product_id: int, delta: int, operation_id: str
    ) -> Any:
        async def invoke() -> Any:
            return await self._command.AdjustProductStock(
                self._pb2.AdjustProductStockRequest(
                    product_id=product_id,
                    delta=delta,
                    operation_id=operation_id,
                ),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_product_internal.with_internal(exc) from exc

        data = resp.data
        return self._row_cls(
            product_id=data.id,
            count_in_stock=data.count_in_stock,
        )


__all__ = ["ProductCommandAdapter", "ProductQueryAdapter"]
