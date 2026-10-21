"""Order item query service. Pagination is normalised once and the normalised values feed both the cache key and the repository call. Reads are cache-first; a miss loads from the DB and populates the cache. Every failure collapses to the service's `Failed to...` sentinel (500), exactly as `errorhandler.HandlerErrorPagination` does — the repository's more specific error is not propagated on this path."""

from __future__ import annotations

from pkg.database.schema.order_item import (
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    GetOrderItemsTrashedRow,
)
from pkg.logger.logger import Logger
from service.order_item.redis.interfaces import OrderItemQueryCache
from service.order_item.repository.interfaces import OrderItemQueryRepository
from shared.errors import (
    err_failed_find_all_order_items,
    err_failed_find_order_item_by_order,
    err_failed_find_order_items_by_active,
    err_failed_find_order_items_by_trashed,
)
from shared.observability import Observability


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    if page <= 0:
        page = 1
    if page_size <= 0:
        page_size = 10
    return page, page_size


class OrderItemQueryServiceImpl:
    def __init__(
        self,
        repo: OrderItemQueryRepository,
        cache: OrderItemQueryCache,
        logger: Logger,
        obs: Observability,
    ) -> None:
        self._repo = repo
        self._cache = cache
        self._logger = logger
        self._obs = obs

    async def find_all(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetOrderItemsRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "order_item.query.find_all", page=page, page_size=page_size
        ):
            cached = await self._cache.get_order_items_all(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_all(search, page, page_size)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to find all order items: {exc}")
                raise err_failed_find_all_order_items from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_order_items_all(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_active(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetOrderItemsActiveRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "order_item.query.find_active", page=page, page_size=page_size
        ):
            cached = await self._cache.get_order_item_active(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_active(search, page, page_size)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to find active order items: {exc}")
                raise err_failed_find_order_items_by_active from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_order_item_active(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_trashed(
        self, search: str, page: int, page_size: int
    ) -> tuple[list[GetOrderItemsTrashedRow], int]:
        page, page_size = normalize_pagination(page, page_size)
        with self._obs.span(
            "order_item.query.find_trashed", page=page, page_size=page_size
        ):
            cached = await self._cache.get_order_item_trashed(page, page_size, search)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_trashed(search, page, page_size)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(f"Failed to find trashed order items: {exc}")
                raise err_failed_find_order_items_by_trashed from exc
            total = rows[0].total_count if rows else 0
            await self._cache.set_order_item_trashed(
                page, page_size, search, rows, total
            )
            return rows, total

    async def find_by_order(
        self, order_id: int
    ) -> list[GetOrderItemsByOrderRow]:
        with self._obs.span("order_item.query.find_by_order", order_id=order_id):
            cached = await self._cache.get_order_items(order_id)
            if cached is not None:
                return cached
            try:
                rows = await self._repo.find_order_item_by_order(order_id)
            except Exception as exc:  # noqa: BLE001 - collapses to one sentinel
                self._logger.error(
                    f"Failed to find order items by order ID: {exc}"
                )
                raise err_failed_find_order_item_by_order from exc
            await self._cache.set_order_items(rows)
            return rows


__all__ = ["OrderItemQueryServiceImpl", "normalize_pagination"]
