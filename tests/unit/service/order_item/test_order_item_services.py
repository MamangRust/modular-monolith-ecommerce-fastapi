"""Unit tests for order item query/command services and cache invalidation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.order_item import (
    CreateOrderItemRow,
    GetOrderItemsActiveRow,
    GetOrderItemsByOrderRow,
    GetOrderItemsRow,
    OrderItem,
    UpdateOrderItemRow,
)
from pkg.logger.logger import Logger
from service.order_item.service.order_item_command_service import (
    OrderItemCommandServiceImpl,
)
from service.order_item.service.order_item_query_service import (
    OrderItemQueryServiceImpl,
    normalize_pagination,
)
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    UpdateOrderItemRecordRequest,
)
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)


def _row(order_item_id: int = 1, total: int = 1) -> GetOrderItemsRow:
    return GetOrderItemsRow(
        order_item_id=order_item_id,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(order_item_id: int = 1, total: int = 1) -> GetOrderItemsActiveRow:
    return GetOrderItemsActiveRow(
        order_item_id=order_item_id,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _by_order_row(order_item_id: int = 1) -> GetOrderItemsByOrderRow:
    return GetOrderItemsByOrderRow(
        order_item_id=order_item_id,
        order_id=10,
        product_id=20,
        quantity=2,
        price=5000,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.by_order_rows: list[GetOrderItemsByOrderRow] = [_by_order_row()]

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_row(total=1)]

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_order_item_by_order(self, order_id):
        self.calls.append(f"find_by_order:{order_id}")
        return self.by_order_rows


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_order_items_all(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_order_items_all(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_order_item_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_order_item_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_order_item_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_order_item_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_order_items(self, order_id):
        return self.store.get(f"order:{order_id}")

    async def set_order_items(self, rows):
        if not rows:
            return
        self.writes.append(f"order:{rows[0].order_id}")
        self.store[f"order:{rows[0].order_id}"] = rows


def _logger() -> Logger:
    return Logger("test", "error")


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> OrderItemQueryServiceImpl:
    logger = _logger()
    return OrderItemQueryServiceImpl(repo, cache, logger, Observability("test", logger))


async def test_normalize_pagination() -> None:
    assert normalize_pagination(0, 0) == (1, 10)
    assert normalize_pagination(-3, -1) == (1, 10)
    assert normalize_pagination(2, 25) == (2, 25)


async def test_find_all_normalizes_and_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 0, 0)

    assert repo.calls == ["find_all::1:10"]
    assert cache.writes == ["all:1:10:"]
    assert total == 1
    assert rows[0].total_count == 1


async def test_find_all_served_from_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    await service.find_all("", 1, 10)
    repo.calls.clear()

    _, total = await service.find_all("", 1, 10)

    assert repo.calls == []
    assert total == 1


async def test_find_active_and_trashed_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)
    cache.store["active:1:10:"] = ([_active_row(order_item_id=1)], 1)
    cache.store["trashed:1:10:"] = ([_active_row(order_item_id=2)], 1)

    active_rows, _ = await service.find_active("", 1, 10)
    trashed_rows, _ = await service.find_trashed("", 1, 10)

    assert repo.calls == []
    assert active_rows[0].order_item_id == 1
    assert trashed_rows[0].order_item_id == 2


async def test_find_by_order_caches_and_is_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows = await service.find_by_order(10)
    assert repo.calls == ["find_by_order:10"]
    assert cache.writes == ["order:10"]
    repo.calls.clear()

    cached = await service.find_by_order(10)
    assert repo.calls == []
    assert cached[0].order_item_id == rows[0].order_item_id


async def test_find_by_order_empty_result_is_not_cached() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    repo.by_order_rows = []
    service = _query_service(repo, cache)

    await service.find_by_order(10)

    assert cache.writes == []


async def test_query_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise RuntimeError("boom")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_all("", 1, 10)
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to find all order items"


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.order_id}:{request.product_id}")
        return CreateOrderItemRow(
            order_item_id=9,
            order_id=request.order_id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=request.price,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.order_item_id}")
        return UpdateOrderItemRow(
            order_item_id=request.order_item_id,
            order_id=10,
            product_id=20,
            quantity=request.quantity,
            price=request.price,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, order_item_id):
        self.calls.append(f"trash:{order_item_id}")
        return OrderItem(
            order_item_id=order_item_id,
            order_id=10,
            product_id=20,
            quantity=2,
            price=5000,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=UPDATED,
        )

    async def restore(self, order_item_id):
        self.calls.append(f"restore:{order_item_id}")
        return OrderItem(
            order_item_id=order_item_id,
            order_id=10,
            product_id=20,
            quantity=2,
            price=5000,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, order_item_id):
        self.calls.append(f"delete:{order_item_id}")
        return True

    async def delete_order_item_by_order_permanent(self, order_id):
        self.calls.append(f"delete_by_order:{order_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True

    async def calculate_total_price(self, order_id):
        self.calls.append(f"total:{order_id}")
        return 12345


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidations = 0

    async def invalidate_order_item_cache(self):
        self.invalidations += 1
        return 1


def _command_service(
    repo: FakeCommandRepo, cache: FakeCommandCache
) -> OrderItemCommandServiceImpl:
    logger = _logger()
    return OrderItemCommandServiceImpl(
        repo, cache, logger, Observability("test", logger)
    )


async def test_create_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.create(
        CreateOrderItemRecordRequest(
            order_id=10, product_id=20, quantity=2, price=5000
        )
    )

    assert row.order_item_id == 9
    assert cache.invalidations == 1


async def test_update_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.update(
        UpdateOrderItemRecordRequest(order_item_id=4, quantity=3, price=6000)
    )

    assert cache.invalidations == 1


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)

    assert cache.invalidations == 3


async def test_bulk_and_by_order_commands_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.restore_all()
    await service.delete_all()
    await service.delete_by_order_permanent(7)

    assert cache.invalidations == 3


async def test_calculate_total_price_does_not_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    total = await service.calculate_total_price(10)

    assert total == 12345
    assert cache.invalidations == 0


async def test_trash_propagates_not_found() -> None:
    class MissingRepo(FakeCommandRepo):
        async def trash(self, order_item_id):
            raise AppError("NOT_FOUND", 404, "order item not found")

    service = _command_service(MissingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.trash(7)
    assert excinfo.value.code == 404


async def test_create_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise RuntimeError("boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.create(
            CreateOrderItemRecordRequest(
                order_id=10, product_id=20, quantity=2, price=5000
            )
        )
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to create order item"


async def test_calculate_total_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def calculate_total_price(self, order_id):
            raise RuntimeError("boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.calculate_total_price(10)
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to calculate total"
