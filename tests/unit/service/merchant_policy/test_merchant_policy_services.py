"""Unit tests for the merchant_policy services (no DB/Redis). Covers the cache-first query service and the command service. Error: the merchant_policy query service remaps reads to its own sentinels (like merchant_business): list failures become `err_failed_find_*_merchant_policies` (500), and `FindByID` maps the repository not-found to `err_merchant_policy_not_found` (404) and every other failure to `err_failed_find_merchant_policy_by_id` (500). The command service remaps only `Create`, `Update` and `RestoreAll`; `Trash`/`Restore`/`DeletePermanent`/ `DeleteAll` propagate the repository error unchanged. NORMALISATION: reports the window `COUNT(*)` as `total_records`, not `len(page)`."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.merchant_policy import (
    CreateMerchantPolicyRow,
    GetMerchantPoliciesActiveRow,
    GetMerchantPoliciesRow,
    GetMerchantPolicyRow,
    MerchantPolicy,
)
from pkg.logger.logger import Logger
from service.merchant_policy.service.merchant_policy_command_service import (
    MerchantPolicyCommandServiceImpl,
)
from service.merchant_policy.service.merchant_policy_query_service import (
    MerchantPolicyQueryServiceImpl,
)
from shared.domain.requests.merchant_policy import (
    CreateMerchantPolicyRequest,
    UpdateMerchantPolicyRequest,
)
from shared.errors import AppError, err_merchant_policy_not_found
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


# ---- query service ----


def _list_row(policy_id: int = 1, total: int = 1) -> GetMerchantPoliciesRow:
    return GetMerchantPoliciesRow(
        merchant_policy_id=policy_id,
        merchant_id=10,
        policy_type="Shipping",
        title="Free Shipping on Orders Above $50",
        description="desc",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
    )


def _active_row(
    policy_id: int = 1, deleted_at: datetime | None = None
) -> GetMerchantPoliciesActiveRow:
    return GetMerchantPoliciesActiveRow(
        merchant_policy_id=policy_id,
        merchant_id=10,
        policy_type="Refund",
        title="30-Day Refund Policy",
        description="desc",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
        merchant_name="Elektronik Store",
        total_count=1,
    )


def _by_id_row(policy_id: int = 1) -> GetMerchantPolicyRow:
    return GetMerchantPolicyRow(
        merchant_policy_id=policy_id,
        merchant_id=10,
        policy_type="Shipping",
        title="Free Shipping on Orders Above $50",
        description="desc",
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

    async def find_by_id(self, merchant_policy_id):
        self.calls.append(f"find_by_id:{merchant_policy_id}")
        return _by_id_row(merchant_policy_id)


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_merchant_policies(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_merchant_policies(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_policies_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_merchant_policies_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_policies_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_merchant_policies_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_policy(self, merchant_policy_id):
        return self.store.get(f"id:{merchant_policy_id}")

    async def set_merchant_policy(self, row):
        self.writes.append(f"id:{row.merchant_policy_id}")
        self.store[f"id:{row.merchant_policy_id}"] = row


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> MerchantPolicyQueryServiceImpl:
    return MerchantPolicyQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 1, 10)
    assert total == 1
    assert cache.writes == ["all:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all("", 1, 10)
    assert repo.calls == []
    assert cached_rows[0].merchant_policy_id == rows[0].merchant_policy_id


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

    with pytest.raises(AppError) as all_exc:
        await service.find_all("", 1, 10)
    assert all_exc.value.code == 500
    # messages are lowercase for merchant_policy (unlike merchant_business).
    assert all_exc.value.message == "failed to fetch all merchant policies"

    with pytest.raises(AppError) as active_exc:
        await service.find_active("", 1, 10)
    assert active_exc.value.code == 500
    assert active_exc.value.message == "failed to fetch active merchant policies"

    with pytest.raises(AppError) as trashed_exc:
        await service.find_trashed("", 1, 10)
    assert trashed_exc.value.code == 500
    assert trashed_exc.value.message == "failed to fetch trashed merchant policies"


async def test_query_find_by_id_maps_not_found_and_other_errors() -> None:
    class NotFoundRepo(FakeQueryRepo):
        async def find_by_id(self, merchant_policy_id):
            raise err_merchant_policy_not_found

    service = _query_service(NotFoundRepo(), FakeQueryCache())
    with pytest.raises(AppError) as not_found_exc:
        await service.find_by_id(1)
    assert not_found_exc.value.code == 404
    assert not_found_exc.value.message == "merchant policy not found"

    class FailingRepo(FakeQueryRepo):
        async def find_by_id(self, merchant_policy_id):
            raise AppError("INTERNAL", 500, "boom")

    failing = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as by_id_exc:
        await failing.find_by_id(1)
    assert by_id_exc.value.code == 500
    assert by_id_exc.value.message == "failed to find merchant policy by id"


async def test_query_empty_page_reports_zero_total() -> None:
    class EmptyRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            return []

    service = _query_service(EmptyRepo(), FakeQueryCache())
    rows, total = await service.find_all("", 1, 10)
    assert rows == []
    assert total == 0


async def test_query_total_comes_from_window_count() -> None:
    # NORMALISATION: used `len(page)`; uses the window COUNT(*).
    class BigRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            return [_list_row(1, total=42), _list_row(2, total=42)]

    service = _query_service(BigRepo(), FakeQueryCache())
    rows, total = await service.find_all("", 1, 10)
    assert len(rows) == 2
    assert total == 42


# ---- command service ----


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.merchant_id}")
        return CreateMerchantPolicyRow(
            merchant_policy_id=9,
            merchant_id=request.merchant_id,
            policy_type=request.policy_type,
            title=request.title,
            description=request.description,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.merchant_policy_id}")
        return CreateMerchantPolicyRow(
            merchant_policy_id=request.merchant_policy_id or 1,
            merchant_id=10,
            policy_type=request.policy_type,
            title=request.title,
            description=request.description,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_policy_id):
        self.calls.append(f"trash:{merchant_policy_id}")
        return MerchantPolicy(
            merchant_policy_id=merchant_policy_id,
            merchant_id=10,
            policy_type="Shipping",
            title="Free Shipping",
            description="desc",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_policy_id):
        self.calls.append(f"restore:{merchant_policy_id}")
        return MerchantPolicy(
            merchant_policy_id=merchant_policy_id,
            merchant_id=10,
            policy_type="Shipping",
            title="Free Shipping",
            description="desc",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_policy_id):
        self.calls.append(f"delete:{merchant_policy_id}")
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

    async def delete_cached_merchant_policy(self, merchant_policy_id: int) -> int:
        self.evicted.append(merchant_policy_id)
        return 1


def _command_service(
    repo: FakeCommandRepo, cache: FakeCommandCache
) -> MerchantPolicyCommandServiceImpl:
    return MerchantPolicyCommandServiceImpl(repo, cache, _logger(), _obs())


def _create_request(merchant_id: int = 10) -> CreateMerchantPolicyRequest:
    return CreateMerchantPolicyRequest(
        merchant_id=merchant_id,
        policy_type="Shipping",
        title="Free Shipping on Orders Above $50",
        description="desc",
    )


def _update_request(policy_id: int = 4) -> UpdateMerchantPolicyRequest:
    return UpdateMerchantPolicyRequest(
        merchant_policy_id=policy_id,
        policy_type="Refund",
        title="30-Day Refund Policy",
        description="desc",
    )


async def test_command_create_does_not_evict_and_remaps_error() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.create(_create_request(7))
    assert row.merchant_policy_id == 9
    assert repo.calls == ["create:7"]
    # merchant_policy Create does NOT evict (unlike merchant_business).
    assert cache.evicted == []

    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("NOT_FOUND", 404, "boom")

    failing = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await failing.create(_create_request())
    assert excinfo.value.code == 500
    assert excinfo.value.message == "failed to create merchant policy"


async def test_command_update_evicts_and_remaps_error() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    row = await service.update(_update_request(4))
    assert row.merchant_policy_id == 4
    assert cache.evicted == [4]

    class FailingRepo(FakeCommandRepo):
        async def update(self, request):
            raise AppError("NOT_FOUND", 404, "boom")

    failing = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await failing.update(_update_request())
    assert excinfo.value.code == 500
    assert excinfo.value.message == "failed to update merchant policy"


async def test_command_trash_restore_delete_propagate_and_evict() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(3)
    await service.restore(3)
    await service.delete_permanent(3)
    assert cache.evicted == [3, 3, 3]

    class FailingRepo(FakeCommandRepo):
        async def trash(self, merchant_policy_id):
            raise AppError("NOT_FOUND", 404, "gone")

        async def restore(self, merchant_policy_id):
            raise AppError("NOT_FOUND", 404, "gone")

        async def delete_permanent(self, merchant_policy_id):
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
    assert excinfo.value.message == "failed to restore all merchant policies"


async def test_command_eviction_matrix() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.create(_create_request())
    await service.update(_update_request(2))
    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    # Create does NOT evict; the rest do.
    assert cache.evicted == [2, 2, 2, 2]

    cache.evicted.clear()
    await service.restore_all()
    await service.delete_all()
    assert cache.evicted == []


__all__ = []
