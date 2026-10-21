"""Unit tests for the merchant_business services (no DB/Redis). Covers the cache-first query service and the command service. Error: unlike merchant_award (which forwards repository errors, #69), the merchant_business query service remaps reads to its own sentinels (like merchant_detail, #76): list failures become `err_failed_find_*_merchant_business` (500), and `FindByID` maps the repository not-found to `err_merchant_business_not_found` (404) and every other failure to `err_failed_find_merchant_business_by_id` (500). The command service remaps only `Create`, `Update` and `RestoreAll`; `Trash`/`Restore`/`DeletePermanent`/ `DeleteAll` propagate the repository error unchanged."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.merchant_business import (
    CreateMerchantBusinessInformationRow,
    GetMerchantBusinessInformationRow,
    GetMerchantsBusinessInformationActiveRow,
    GetMerchantsBusinessInformationRow,
    MerchantBusinessInformation,
)
from pkg.logger.logger import Logger
from service.merchant_business.service.merchant_business_command_service import (
    MerchantBusinessCommandServiceImpl,
)
from service.merchant_business.service.merchant_business_query_service import (
    MerchantBusinessQueryServiceImpl,
)
from shared.domain.requests.merchant_business import (
    CreateMerchantBusinessInformationRequest,
    UpdateMerchantBusinessInformationRequest,
)
from shared.errors import AppError, err_merchant_business_not_found
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


# ---- query service ----


def _list_row(
    business_id: int = 1, total: int = 1
) -> GetMerchantsBusinessInformationRow:
    return GetMerchantsBusinessInformationRow(
        merchant_business_info_id=business_id,
        merchant_id=10,
        business_type="Toko Elektronik",
        tax_id="01.234.567.8-999.000",
        established_year=2010,
        number_of_employees=15,
        website_url="https://technostore.com",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
    )


def _active_row(
    business_id: int = 1, deleted_at: datetime | None = None
) -> GetMerchantsBusinessInformationActiveRow:
    return GetMerchantsBusinessInformationActiveRow(
        merchant_business_info_id=business_id,
        merchant_id=10,
        business_type="Toko Elektronik",
        tax_id=None,
        established_year=None,
        number_of_employees=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        merchant_name="Elektronik Store",
        total_count=1,
    )


def _by_id_row(business_id: int = 1) -> GetMerchantBusinessInformationRow:
    return GetMerchantBusinessInformationRow(
        merchant_business_info_id=business_id,
        merchant_id=10,
        business_type="Toko Elektronik",
        tax_id=None,
        established_year=None,
        number_of_employees=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_list_row()]

    async def find_active(self, search, page, page_size):
        self.calls.append("find_active")
        return [_active_row()]

    async def find_trashed(self, search, page, page_size):
        self.calls.append("find_trashed")
        return [_active_row(deleted_at=DELETED)]

    async def find_by_id(self, merchant_business_info_id):
        self.calls.append(f"find_by_id:{merchant_business_info_id}")
        return _by_id_row(merchant_business_info_id)


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_merchant_businesses(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_merchant_businesses(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_businesses_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_merchant_businesses_active(
        self, page, page_size, search, rows, total
    ):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_businesses_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_merchant_businesses_trashed(
        self, page, page_size, search, rows, total
    ):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_business(self, merchant_business_info_id):
        return self.store.get(f"id:{merchant_business_info_id}")

    async def set_merchant_business(self, row):
        self.writes.append(f"id:{row.merchant_business_info_id}")
        self.store[f"id:{row.merchant_business_info_id}"] = row


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> MerchantBusinessQueryServiceImpl:
    return MerchantBusinessQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 1, 10)
    assert total == 1
    assert cache.writes == ["all:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all("", 1, 10)
    assert repo.calls == []
    assert cached_rows[0].merchant_business_info_id == rows[0].merchant_business_info_id


async def test_query_find_active_and_trashed_cache() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    await service.find_active("", 1, 10)
    await service.find_trashed("", 1, 10)
    assert repo.calls == ["find_active", "find_trashed"]

    repo.calls.clear()
    active, _ = await service.find_active("", 1, 10)
    trashed, _ = await service.find_trashed("", 1, 10)
    assert repo.calls == []
    assert active[0].deleted_at is None
    assert trashed[0].deleted_at == DELETED


async def test_query_find_by_id_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    await service.find_by_id(5)
    assert repo.calls == ["find_by_id:5"]
    assert cache.writes == ["id:5"]


async def test_query_list_failures_remap_to_service_sentinels() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "boom")

        async def find_active(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "boom")

        async def find_trashed(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "boom")

    service = _query_service(FailingRepo(), FakeQueryCache())

    # Unlike merchant_award, the merchant_business query service remaps reads
    # (like merchant_detail, #76), so the 404 becomes its own 500 sentinel.
    with pytest.raises(AppError) as all_exc:
        await service.find_all("", 1, 10)
    assert all_exc.value.code == 500
    assert all_exc.value.message == "Failed to fetch all merchant businesses"

    with pytest.raises(AppError) as active_exc:
        await service.find_active("", 1, 10)
    assert active_exc.value.code == 500
    assert active_exc.value.message == "Failed to fetch active merchant businesses"

    with pytest.raises(AppError) as trashed_exc:
        await service.find_trashed("", 1, 10)
    assert trashed_exc.value.code == 500
    assert trashed_exc.value.message == "Failed to fetch trashed merchant businesses"


async def test_query_find_by_id_maps_not_found_and_other_errors() -> None:
    class NotFoundRepo(FakeQueryRepo):
        async def find_by_id(self, merchant_business_info_id):
            raise err_merchant_business_not_found

    service = _query_service(NotFoundRepo(), FakeQueryCache())
    with pytest.raises(AppError) as not_found_exc:
        await service.find_by_id(1)
    # The repository's 404 sentinel is preserved.
    assert not_found_exc.value.code == 404
    assert not_found_exc.value.message == "merchant business not found"

    class FailingRepo(FakeQueryRepo):
        async def find_by_id(self, merchant_business_info_id):
            raise AppError("INTERNAL", 500, "boom")

    failing = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as by_id_exc:
        await failing.find_by_id(1)
    assert by_id_exc.value.code == 500
    assert by_id_exc.value.message == "Failed to find merchant business by ID"


async def test_query_empty_page_reports_zero_total() -> None:
    class EmptyRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            return []

    service = _query_service(EmptyRepo(), FakeQueryCache())
    rows, total = await service.find_all("", 1, 10)
    assert rows == []
    assert total == 0


# ---- command service ----


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.merchant_id}")
        return CreateMerchantBusinessInformationRow(
            merchant_business_info_id=9,
            merchant_id=request.merchant_id,
            business_type=request.business_type,
            tax_id=request.tax_id,
            established_year=request.established_year,
            number_of_employees=request.number_of_employees,
            website_url=request.website_url or None,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.merchant_business_info_id}")
        return CreateMerchantBusinessInformationRow(
            merchant_business_info_id=request.merchant_business_info_id or 1,
            merchant_id=10,
            business_type=request.business_type,
            tax_id=request.tax_id,
            established_year=request.established_year,
            number_of_employees=request.number_of_employees,
            website_url=request.website_url or None,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_business_info_id):
        self.calls.append(f"trash:{merchant_business_info_id}")
        return MerchantBusinessInformation(
            merchant_business_info_id=merchant_business_info_id,
            merchant_id=10,
            business_type="Toko Elektronik",
            tax_id=None,
            established_year=None,
            number_of_employees=None,
            website_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_business_info_id):
        self.calls.append(f"restore:{merchant_business_info_id}")
        return MerchantBusinessInformation(
            merchant_business_info_id=merchant_business_info_id,
            merchant_id=10,
            business_type="Toko Elektronik",
            tax_id=None,
            established_year=None,
            number_of_employees=None,
            website_url=None,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_business_info_id):
        self.calls.append(f"delete:{merchant_business_info_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


class FakeCommandCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []

    async def delete_cached_merchant_business(
        self, merchant_business_info_id: int
    ) -> int:
        self.evicted.append(merchant_business_info_id)
        return 1


def _command_service(
    repo: FakeCommandRepo, cache: FakeCommandCache
) -> MerchantBusinessCommandServiceImpl:
    return MerchantBusinessCommandServiceImpl(repo, cache, _logger(), _obs())


def _create_request(
    merchant_id: int = 10,
) -> CreateMerchantBusinessInformationRequest:
    return CreateMerchantBusinessInformationRequest(
        merchant_id=merchant_id,
        business_type="Toko Elektronik",
        tax_id="01.234.567.8-999.000",
        established_year=2010,
        number_of_employees=15,
        website_url="https://technostore.com",
    )


def _update_request(
    business_id: int = 4,
) -> UpdateMerchantBusinessInformationRequest:
    return UpdateMerchantBusinessInformationRequest(
        merchant_business_info_id=business_id,
        business_type="Retail Gadget",
        tax_id="04.567.890.1-666.000",
        established_year=2018,
        number_of_employees=8,
        website_url="https://gadgethub.com",
    )


async def test_command_create_evicts_new_id_and_remaps_error() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.create(_create_request(7))
    assert row.merchant_business_info_id == 9
    assert repo.calls == ["create:7"]
    # evicts the new row's by-id key even though it was never cached.
    assert cache.evicted == [9]

    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("NOT_FOUND", 404, "boom")

    failing = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await failing.create(_create_request())
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to create merchant business"


async def test_command_update_evicts_and_remaps_error() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.update(_update_request(4))
    assert row.merchant_business_info_id == 4
    assert cache.evicted == [4]

    class FailingRepo(FakeCommandRepo):
        async def update(self, request):
            raise AppError("NOT_FOUND", 404, "boom")

    failing = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await failing.update(_update_request())
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to update merchant business"


async def test_command_trash_restore_delete_propagate_and_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(3)
    await service.restore(3)
    await service.delete_permanent(3)
    assert cache.evicted == [3, 3, 3]

    class FailingRepo(FakeCommandRepo):
        async def trash(self, merchant_business_info_id):
            raise AppError("NOT_FOUND", 404, "gone")

        async def restore(self, merchant_business_info_id):
            raise AppError("NOT_FOUND", 404, "gone")

        async def delete_permanent(self, merchant_business_info_id):
            raise AppError("NOT_FOUND", 404, "gone")

        async def delete_all(self):
            raise AppError("INTERNAL", 500, "boom")

    failing = _command_service(FailingRepo(), FakeCommandCache())
    for call in (
        failing.trash(1),
        failing.restore(1),
        failing.delete_permanent(1),
    ):
        with pytest.raises(AppError) as excinfo:
            await call
        # These paths propagate the repository error unchanged.
        assert excinfo.value.code == 404
        assert excinfo.value.message == "gone"

    with pytest.raises(AppError) as delete_all_exc:
        await failing.delete_all()
    assert delete_all_exc.value.code == 500
    assert delete_all_exc.value.message == "boom"


async def test_command_restore_all_remaps_error() -> None:
    class FailingRepo(FakeCommandRepo):
        async def restore_all(self):
            raise AppError("NOT_FOUND", 404, "boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.restore_all()
    assert excinfo.value.code == 500
    assert excinfo.value.message == "Failed to restore all merchant businesses"


async def test_command_eviction_matrix() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    created = await service.create(_create_request())
    await service.update(_update_request(2))
    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    assert cache.evicted == [created.merchant_business_info_id, 2, 2, 2, 2]

    cache.evicted.clear()
    await service.restore_all()
    await service.delete_all()
    assert cache.evicted == []


__all__ = []
