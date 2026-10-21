"""Unit tests for shipping address query/command services and cache invalidation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.shipping_address import (
    CreateShippingAddressRow,
    GetShippingAddressActiveRow,
    GetShippingAddressByOrderIDRow,
    GetShippingAddressRow,
    GetShippingByIDRow,
    ShippingAddress,
    UpdateShippingAddressRow,
)
from pkg.logger.logger import Logger
from service.shipping_address.service.shipping_address_command_service import (
    ShippingAddressCommandServiceImpl,
)
from service.shipping_address.service.shipping_address_query_service import (
    ShippingAddressQueryServiceImpl,
    normalize_pagination,
)
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    UpdateShippingAddressRequest,
)
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 10, 0, 0)


def _row(shipping_address_id: int = 1, total: int = 1) -> GetShippingAddressRow:
    return GetShippingAddressRow(
        shipping_address_id=shipping_address_id,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _active_row(shipping_address_id: int = 1, total: int = 1) -> GetShippingAddressActiveRow:
    return GetShippingAddressActiveRow(
        shipping_address_id=shipping_address_id,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=total,
    )


def _by_id_row(shipping_address_id: int = 1) -> GetShippingByIDRow:
    return GetShippingByIDRow(
        shipping_address_id=shipping_address_id,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
    )


def _by_order_row(shipping_address_id: int = 1) -> GetShippingAddressByOrderIDRow:
    return GetShippingAddressByOrderIDRow(
        shipping_address_id=shipping_address_id,
        order_id=10,
        alamat="Jl. Merdeka 1",
        provinsi="DKI Jakarta",
        negara="Indonesia",
        kota="Jakarta",
        courier="JNE",
        shipping_method="REG",
        shipping_cost=12.75,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_row(total=1)]

    async def find_active(self, search, page, page_size):
        self.calls.append(f"find_active:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_trashed(self, search, page, page_size):
        self.calls.append(f"find_trashed:{search}:{page}:{page_size}")
        return [_active_row(total=1)]

    async def find_by_id(self, shipping_id):
        self.calls.append(f"find_by_id:{shipping_id}")
        return _by_id_row(shipping_id)

    async def find_by_order(self, order_id):
        self.calls.append(f"find_by_order:{order_id}")
        return _by_order_row()


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_shipping_address_all(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_shipping_address_all(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_shipping_address_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_shipping_address_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_shipping_address_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_shipping_address_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_cached_shipping_address(self, shipping_id):
        return self.store.get(f"id:{shipping_id}")

    async def set_cached_shipping_address(self, row):
        if row is None:
            return
        self.writes.append(f"id:{row.shipping_address_id}")
        self.store[f"id:{row.shipping_address_id}"] = row

    async def get_cached_shipping_address_by_order(self, order_id):
        return self.store.get(f"order:{order_id}")

    async def set_cached_shipping_address_by_order(self, row):
        if row is None:
            return
        self.writes.append(f"order:{row.order_id}")
        self.store[f"order:{row.order_id}"] = row


def _logger() -> Logger:
    return Logger("test", "error")


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> ShippingAddressQueryServiceImpl:
    logger = _logger()
    return ShippingAddressQueryServiceImpl(
        repo, cache, logger, Observability("test", logger)
    )


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
    cache.store["active:1:10:"] = ([_active_row(shipping_address_id=1)], 1)
    cache.store["trashed:1:10:"] = ([_active_row(shipping_address_id=2)], 1)

    active_rows, _ = await service.find_active("", 1, 10)
    trashed_rows, _ = await service.find_trashed("", 1, 10)

    assert repo.calls == []
    assert active_rows[0].shipping_address_id == 1
    assert trashed_rows[0].shipping_address_id == 2


async def test_find_by_id_caches_and_is_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    row = await service.find_by_id(10)
    assert repo.calls == ["find_by_id:10"]
    assert cache.writes == ["id:10"]
    repo.calls.clear()

    cached = await service.find_by_id(10)
    assert repo.calls == []
    assert cached.shipping_address_id == row.shipping_address_id


async def test_find_by_order_caches_and_is_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    row = await service.find_by_order(10)
    assert repo.calls == ["find_by_order:10"]
    assert cache.writes == ["order:10"]
    repo.calls.clear()

    cached = await service.find_by_order(10)
    assert repo.calls == []
    assert cached.shipping_address_id == row.shipping_address_id


async def test_query_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise RuntimeError("boom")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_all("", 1, 10)
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to fetch all shipping addresses"


async def test_find_by_id_propagates_not_found() -> None:
    class MissingRepo(FakeQueryRepo):
        async def find_by_id(self, shipping_id):
            raise AppError("NOT_FOUND", 404, "shipping address not found")

    service = _query_service(MissingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_by_id(999)
    assert excinfo.value.code == 404


async def test_find_by_order_propagates_not_found() -> None:
    class MissingRepo(FakeQueryRepo):
        async def find_by_order(self, order_id):
            raise AppError("NOT_FOUND", 404, "shipping address not found")

    service = _query_service(MissingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_by_order(999)
    assert excinfo.value.code == 404


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.order_id}")
        return CreateShippingAddressRow(
            shipping_address_id=9,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=request.shipping_cost,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.shipping_id}")
        return UpdateShippingAddressRow(
            shipping_address_id=request.shipping_id,
            order_id=request.order_id,
            alamat=request.alamat,
            provinsi=request.provinsi,
            negara=request.negara,
            kota=request.kota,
            courier=request.courier,
            shipping_method=request.shipping_method,
            shipping_cost=request.shipping_cost,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, shipping_id):
        self.calls.append(f"trash:{shipping_id}")
        return ShippingAddress(
            shipping_address_id=shipping_id,
            order_id=10,
            alamat="Jl. Merdeka 1",
            provinsi="DKI Jakarta",
            negara="Indonesia",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12.75,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, shipping_id):
        self.calls.append(f"restore:{shipping_id}")
        return ShippingAddress(
            shipping_address_id=shipping_id,
            order_id=10,
            alamat="Jl. Merdeka 1",
            provinsi="DKI Jakarta",
            negara="Indonesia",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12.75,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, shipping_id):
        self.calls.append(f"delete:{shipping_id}")
        return True

    async def delete_by_order_id_permanent(self, order_id):
        self.calls.append(f"delete_by_order:{order_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.invalidations = 0

    async def delete_shipping_address_cache(self, shipping_id: int) -> int:
        self.invalidations += 1
        return 1

    async def invalidate_shipping_address_cache(self):
        self.invalidations += 1
        return 1


def _command_service(
    repo: FakeCommandRepo, cache: FakeCommandCache
) -> ShippingAddressCommandServiceImpl:
    logger = _logger()
    return ShippingAddressCommandServiceImpl(
        repo, cache, logger, Observability("test", logger)
    )


async def test_create_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.create(
        CreateShippingAddressRequest(
            order_id=10,
            alamat="Jl. Merdeka 1",
            provinsi="DKI Jakarta",
            negara="Indonesia",
            kota="Jakarta",
            courier="JNE",
            shipping_method="REG",
            shipping_cost=12000,
        )
    )

    assert row.shipping_address_id == 9
    assert cache.invalidations == 1


async def test_update_invalidates_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.update(
        UpdateShippingAddressRequest(shipping_id=4, kota="Bandung")
    )

    assert cache.invalidations == 1


async def test_trash_restore_delete_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)

    assert cache.invalidations == 3


async def test_delete_all_and_delete_by_order_invalidate() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.delete_all()
    await service.delete_by_order_id_permanent(7)

    assert cache.invalidations == 2


async def test_restore_all_does_not_invalidate() -> None:
    """RestoreAll forgets the cache invalidation."""
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.restore_all()

    assert cache.invalidations == 0


async def test_trash_propagates_not_found() -> None:
    class MissingRepo(FakeCommandRepo):
        async def trash(self, shipping_id):
            raise AppError("NOT_FOUND", 404, "shipping address not found")

    service = _command_service(MissingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.trash(7)
    assert excinfo.value.code == 404


async def test_delete_all_propagates_repository_error() -> None:
    class MissingRepo(FakeCommandRepo):
        async def delete_all(self):
            raise AppError("NOT_FOUND", 404, "shipping address not found")

    service = _command_service(MissingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.delete_all()
    assert excinfo.value.code == 404


async def test_create_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise RuntimeError("boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.create(CreateShippingAddressRequest(order_id=10))
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to create shipping address"


async def test_update_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def update(self, request):
            raise RuntimeError("boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.update(UpdateShippingAddressRequest(shipping_id=1))
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to update shipping address"


async def test_delete_by_order_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def delete_by_order_id_permanent(self, order_id):
            raise RuntimeError("boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.delete_by_order_id_permanent(7)
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to permanently delete shipping address"


async def test_restore_all_failure_collapses_to_sentinel() -> None:
    class FailingRepo(FakeCommandRepo):
        async def restore_all(self):
            raise RuntimeError("boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.restore_all()
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to restore all shipping addresses"
