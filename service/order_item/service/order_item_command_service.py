"""Order item command service. Every mutation invalidates the `order_item:*` cache after the write commits."""

from __future__ import annotations

from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    OrderItem,
    UpdateOrderItemRow,
)
from pkg.logger.logger import Logger
from service.order_item.redis.interfaces import OrderItemCommandCache
from service.order_item.repository.interfaces import OrderItemCommandRepository
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.errors import (
    err_failed_calculate_total,
    err_failed_create_order_item,
    err_failed_restore_all_order_item,
    err_failed_update_order_item,
)
from shared.observability import Observability


class OrderItemCommandServiceImpl:
    def __init__(
        self,
        repo: OrderItemCommandRepository,
        cache: OrderItemCommandCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def create(
        self, request: CreateOrderItemRecordRequest
    ) -> CreateOrderItemRow:
        with self._obs.span(
            "order_item.command.create",
            order_id=request.order_id,
            product_id=request.product_id,
        ):
            try:
                row = await self._repo.create(request)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to create order item: {exc}")
                raise err_failed_create_order_item from exc
            await self._cache.invalidate_order_item_cache()
            self._logger.info(
                "order item created", order_item_id=row.order_item_id
            )
            return row

    async def update(
        self, request: UpdateOrderItemRecordRequest
    ) -> UpdateOrderItemRow:
        with self._obs.span(
            "order_item.command.update", order_item_id=request.order_item_id
        ):
            try:
                row = await self._repo.update(request)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to update order item: {exc}")
                raise err_failed_update_order_item from exc
            await self._cache.invalidate_order_item_cache()
            self._logger.info(
                "order item updated", order_item_id=request.order_item_id
            )
            return row

    async def trash(self, order_item_id: int) -> OrderItem:
        with self._obs.span("order_item.command.trash", order_item_id=order_item_id):
            row = await self._repo.trash(order_item_id)
            await self._cache.invalidate_order_item_cache()
            self._logger.info("order item trashed", order_item_id=order_item_id)
            return row

    async def restore(self, order_item_id: int) -> OrderItem:
        with self._obs.span("order_item.command.restore", order_item_id=order_item_id):
            row = await self._repo.restore(order_item_id)
            await self._cache.invalidate_order_item_cache()
            self._logger.info("order item restored", order_item_id=order_item_id)
            return row

    async def delete_permanent(self, order_item_id: int) -> bool:
        with self._obs.span(
            "order_item.command.delete_permanent", order_item_id=order_item_id
        ):
            success = await self._repo.delete_permanent(order_item_id)
            await self._cache.invalidate_order_item_cache()
            self._logger.info(
                "order item deleted permanently", order_item_id=order_item_id
            )
            return success

    async def delete_by_order_permanent(self, order_id: int) -> bool:
        with self._obs.span(
            "order_item.command.delete_by_order_permanent", order_id=order_id
        ):
            success = await self._repo.delete_order_item_by_order_permanent(order_id)
            await self._cache.invalidate_order_item_cache()
            self._logger.info(
                "order items deleted by order permanently", order_id=order_id
            )
            return success

    async def restore_all(self) -> bool:
        with self._obs.span("order_item.command.restore_all"):
            try:
                success = await self._repo.restore_all()
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to restore all order items: {exc}")
                raise err_failed_restore_all_order_item from exc
            await self._cache.invalidate_order_item_cache()
            self._logger.info("all order items restored")
            return success

    async def delete_all(self) -> bool:
        with self._obs.span("order_item.command.delete_all"):
            success = await self._repo.delete_all()
            await self._cache.invalidate_order_item_cache()
            self._logger.info("all order items deleted permanently")
            return success

    async def calculate_total_price(self, order_id: int) -> int:
        with self._obs.span(
            "order_item.command.calculate_total_price", order_id=order_id
        ):
            try:
                total = await self._repo.calculate_total_price(order_id)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to calculate total: {exc}")
                raise err_failed_calculate_total from exc
            self._logger.info(
                "total price calculated", order_id=order_id, total_price=total
            )
            return total


__all__ = ["OrderItemCommandServiceImpl"]
