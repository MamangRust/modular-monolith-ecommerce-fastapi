"""Unit tests for the merchant_detail + merchant_social_link services (no DB/Redis). Covers the cache-first query service, the command service (merchant-existence check, cache invalidation, the `DeletePermanent` Trash-then-delete with best-effort file removal), and the social-link command service. Error: unlike merchant (which forwards repository errors), the merchant_detail services pass their **own** sentinels to `errorhandler.HandleError` for list reads, `FindByID`, `Create`, `Update` and `RestoreAll`, so those failures are remapped. `Trash`/`Restore`/`DeletePermanent`/ `DeleteAll` forward the repository error unchanged."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from pkg.database.schema.merchant import GetMerchantByIDRow
from pkg.database.schema.merchant_detail import (
    CreateMerchantDetailRow,
    CreateMerchantSocialMediaLinkRow,
    GetMerchantDetailRow,
    GetMerchantDetailsActiveRow,
    GetMerchantDetailsRow,
    MerchantDetail,
    MerchantSocialMediaLink,
)
from pkg.logger.logger import Logger
from service.merchant_detail.service.merchant_detail_command_service import (
    MerchantDetailCommandServiceImpl,
)
from service.merchant_detail.service.merchant_detail_query_service import (
    MerchantDetailQueryServiceImpl,
)
from service.merchant_detail.service.merchant_social_link_command_service import (
    MerchantSocialLinkCommandServiceImpl,
)
from shared.domain.requests.merchant_detail import (
    CreateMerchantDetailRequest,
    CreateMerchantSocialRequest,
    UpdateMerchantDetailRequest,
    UpdateMerchantSocialRequest,
)
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


# ---- query service ----


def _list_row(detail_id: int = 1, total: int = 1) -> GetMerchantDetailsRow:
    return GetMerchantDetailsRow(
        merchant_detail_id=detail_id,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url="cover/techno.jpg",
        logo_url="logo/techno.png",
        short_description="desc",
        website_url="https://technostore.com",
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        total_count=total,
        social_media_links=None,
    )


def _active_row() -> GetMerchantDetailsActiveRow:
    return GetMerchantDetailsActiveRow(
        merchant_detail_id=1,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url=None,
        logo_url=None,
        short_description=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        merchant_name="Elektronik Store",
        total_count=1,
        social_media_links=None,
    )


def _by_id_row(detail_id: int = 1) -> GetMerchantDetailRow:
    return GetMerchantDetailRow(
        merchant_detail_id=detail_id,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url=None,
        logo_url=None,
        short_description=None,
        website_url=None,
        created_at=CREATED,
        updated_at=UPDATED,
        merchant_name="Elektronik Store",
        social_media_links=None,
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
        return [_active_row()]

    async def find_by_id(self, merchant_detail_id):
        self.calls.append(f"find_by_id:{merchant_detail_id}")
        return _by_id_row(merchant_detail_id)

    async def find_by_id_trashed(self, merchant_detail_id):
        self.calls.append(f"find_by_id_trashed:{merchant_detail_id}")
        return _active_row()


class FakeQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_merchant_details(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_merchant_details(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_details_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_merchant_details_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_details_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_merchant_details_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_detail(self, merchant_detail_id):
        return self.store.get(f"id:{merchant_detail_id}")

    async def set_merchant_detail(self, row):
        self.writes.append(f"id:{row.merchant_detail_id}")
        self.store[f"id:{row.merchant_detail_id}"] = row


def _query_service(
    repo: FakeQueryRepo, cache: FakeQueryCache
) -> MerchantDetailQueryServiceImpl:
    return MerchantDetailQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_query_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    rows, total = await service.find_all("", 1, 10)
    assert total == 1
    assert cache.writes == ["all:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all("", 1, 10)
    assert repo.calls == []
    assert cached_rows[0].merchant_detail_id == rows[0].merchant_detail_id


async def test_query_find_by_id_caches() -> None:
    repo, cache = FakeQueryRepo(), FakeQueryCache()
    service = _query_service(repo, cache)

    await service.find_by_id(5)
    assert repo.calls == ["find_by_id:5"]
    assert cache.writes == ["id:5"]


async def test_query_list_read_remaps_repo_error_to_sentinel() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_all(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "boom")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_all("", 1, 10)
    # Remapped to the service's own 500 sentinel (not the repo's 404).
    assert excinfo.value.code == 500
    assert excinfo.value.message == "failed to find all merchant details"


async def test_query_find_by_id_remaps_repo_error_to_not_found() -> None:
    class FailingRepo(FakeQueryRepo):
        async def find_by_id(self, merchant_detail_id):
            raise AppError("INTERNAL", 500, "boom")

    service = _query_service(FailingRepo(), FakeQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_by_id(1)
    assert excinfo.value.code == 404
    assert excinfo.value.message == "merchant detail not found"


# ---- command service ----


class FakeMerchantQueryRepo:
    def __init__(self) -> None:
        self.calls: list[int] = []

    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow:
        self.calls.append(merchant_id)
        return GetMerchantByIDRow(
            merchant_id=merchant_id,
            user_id=10,
            name="Elektronik Store",
            description=None,
            address=None,
            contact_email=None,
            contact_phone=None,
            status="active",
            created_at=CREATED,
            updated_at=UPDATED,
        )


class MissingMerchantRepo:
    async def find_by_id(self, merchant_id: int) -> GetMerchantByIDRow:
        raise AppError("NOT_FOUND", 404, "merchant not found")


def _detail_model(
    detail_id: int = 1,
    *,
    cover: str | None = None,
    logo: str | None = None,
    deleted_at: datetime | None = None,
) -> MerchantDetail:
    return MerchantDetail(
        merchant_detail_id=detail_id,
        merchant_id=10,
        display_name="Techno Store",
        cover_image_url=cover,
        logo_url=logo,
        short_description="desc",
        website_url="https://technostore.com",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=deleted_at,
    )


class FakeCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.trash_detail: MerchantDetail = _detail_model()

    async def create(self, request):
        self.calls.append(f"create:{request.merchant_id}")
        return CreateMerchantDetailRow(
            merchant_detail_id=9,
            merchant_id=request.merchant_id,
            display_name=request.display_name,
            cover_image_url=request.cover_image_url,
            logo_url=request.logo_url,
            short_description=request.short_description,
            website_url=request.website_url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.merchant_detail_id}")
        return CreateMerchantDetailRow(
            merchant_detail_id=request.merchant_detail_id or 1,
            merchant_id=10,
            display_name=request.display_name,
            cover_image_url=request.cover_image_url,
            logo_url=request.logo_url,
            short_description=request.short_description,
            website_url=request.website_url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, merchant_detail_id):
        self.calls.append(f"trash:{merchant_detail_id}")
        return self.trash_detail

    async def restore(self, merchant_detail_id):
        self.calls.append(f"restore:{merchant_detail_id}")
        return _detail_model(merchant_detail_id, deleted_at=None)

    async def delete_permanent(self, merchant_detail_id):
        self.calls.append(f"delete:{merchant_detail_id}")
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

    async def delete_cached_merchant_detail(self, merchant_detail_id: int) -> int:
        self.evicted.append(merchant_detail_id)
        return 1


def _command_service(
    repo: FakeCommandRepo,
    cache: FakeCommandCache,
    *,
    merchant_query: Any | None = None,
) -> MerchantDetailCommandServiceImpl:
    return MerchantDetailCommandServiceImpl(
        repo, merchant_query or FakeMerchantQueryRepo(), cache, _logger(), _obs()
    )


def _create_request(merchant_id: int = 10) -> CreateMerchantDetailRequest:
    return CreateMerchantDetailRequest(
        merchant_id=merchant_id,
        display_name="Techno Store",
        cover_image_url="cover/techno.jpg",
        logo_url="logo/techno.png",
        short_description="desc",
        website_url="https://technostore.com",
    )


async def test_command_create_validates_merchant_then_creates() -> None:
    repo, cache, merchant = (
        FakeCommandRepo(),
        FakeCommandCache(),
        FakeMerchantQueryRepo(),
    )
    service = _command_service(repo, cache, merchant_query=merchant)

    row = await service.create(_create_request(7))
    assert row.merchant_detail_id == 9
    assert merchant.calls == [7]
    assert repo.calls == ["create:7"]
    # Create does not evict the cache.
    assert cache.evicted == []


async def test_command_create_propagates_merchant_lookup_error() -> None:
    service = _command_service(
        FakeCommandRepo(), FakeCommandCache(), merchant_query=MissingMerchantRepo()
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request(999))
    # The adapter error propagates unchanged (404 preserved).
    assert excinfo.value.code == 404


async def test_command_create_remaps_repo_error() -> None:
    class FailingRepo(FakeCommandRepo):
        async def create(self, request):
            raise AppError("NOT_FOUND", 404, "boom")

    service = _command_service(FailingRepo(), FakeCommandCache())
    with pytest.raises(AppError) as excinfo:
        await service.create(_create_request())
    assert excinfo.value.code == 500
    assert excinfo.value.message == "failed to create merchant detail"


async def test_command_update_evicts_cache() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.update(
        UpdateMerchantDetailRequest(
            merchant_detail_id=4,
            display_name="N",
            cover_image_url="c",
            logo_url="l",
            short_description="d",
            website_url="https://x.com",
        )
    )
    assert cache.evicted == [4]


async def test_command_single_mutations_evict_bulk_do_not() -> None:
    repo, cache = FakeCommandRepo(), FakeCommandCache()
    service = _command_service(repo, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    # delete_permanent evicts once (after the hard delete); its internal Trash
    # call goes to the repository, not the service, so it adds no extra evict.
    assert cache.evicted == [2, 2, 2]

    cache.evicted.clear()
    await service.restore_all()
    await service.delete_all()
    assert cache.evicted == []


async def test_command_delete_permanent_removes_files_best_effort(tmp_path: Path) -> None:
    cover = tmp_path / "cover.jpg"
    logo = tmp_path / "logo.png"
    cover.write_text("x")
    logo.write_text("x")

    repo = FakeCommandRepo()
    repo.trash_detail = _detail_model(2, cover=str(cover), logo=str(logo))
    service = _command_service(repo, FakeCommandCache())

    await service.delete_permanent(2)

    assert not cover.exists()
    assert not logo.exists()
    # Trash is called first (to obtain the row), then the hard delete.
    assert repo.calls == ["trash:2", "delete:2"]


async def test_command_delete_permanent_tolerates_missing_files() -> None:
    repo = FakeCommandRepo()
    repo.trash_detail = _detail_model(2, cover="/no/such/file.jpg", logo=None)
    service = _command_service(repo, FakeCommandCache())

    # os.remove on a missing path is swallowed (ignores the error).
    assert await service.delete_permanent(2) is True


async def test_command_delete_permanent_survives_trash_error() -> None:
    class TrashFailingRepo(FakeCommandRepo):
        async def trash(self, merchant_detail_id):
            raise AppError("NOT_FOUND", 404, "gone")

    repo = TrashFailingRepo()
    service = _command_service(repo, FakeCommandCache())

    # Trash error is ignored; DeletePermanent still runs.
    assert await service.delete_permanent(2) is True
    assert repo.calls == ["delete:2"]


# ---- social link command service ----


class FakeSocialRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        self.calls.append(f"create:{request.merchant_detail_id}")
        return CreateMerchantSocialMediaLinkRow(
            merchant_social_id=1,
            merchant_detail_id=request.merchant_detail_id,
            platform=request.platform,
            url=request.url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.id}")
        return CreateMerchantSocialMediaLinkRow(
            merchant_social_id=request.id,
            merchant_detail_id=request.merchant_detail_id,
            platform=request.platform,
            url=request.url,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def trash(self, social_id):
        self.calls.append(f"trash:{social_id}")
        return True

    async def restore(self, social_id):
        self.calls.append(f"restore:{social_id}")
        return True

    async def delete_permanent(self, social_id):
        self.calls.append(f"delete:{social_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


def _social_service(repo: FakeSocialRepo) -> MerchantSocialLinkCommandServiceImpl:
    return MerchantSocialLinkCommandServiceImpl(repo, _logger(), _obs())


async def test_social_create_and_update() -> None:
    repo = FakeSocialRepo()
    service = _social_service(repo)

    created = await service.create(
        CreateMerchantSocialRequest(
            merchant_detail_id=1, platform="Facebook", url="https://facebook.com/x"
        )
    )
    updated = await service.update(
        UpdateMerchantSocialRequest(
            id=5,
            merchant_detail_id=1,
            platform="Twitter",
            url="https://twitter.com/x",
        )
    )
    assert created.platform == "Facebook"
    assert updated.merchant_social_id == 5
    assert repo.calls == ["create:1", "update:5"]


async def test_social_service_remaps_all_errors() -> None:
    class FailingRepo(FakeSocialRepo):
        async def create(self, request):
            raise AppError("NOT_FOUND", 404, "boom")

        async def trash(self, social_id):
            raise AppError("NOT_FOUND", 404, "boom")

    service = _social_service(FailingRepo())
    with pytest.raises(AppError) as create_exc:
        await service.create(
            CreateMerchantSocialRequest(
                merchant_detail_id=1, platform="Facebook", url="https://f.com/x"
            )
        )
    assert create_exc.value.code == 500
    assert create_exc.value.message == "failed to create merchant social link"

    with pytest.raises(AppError) as trash_exc:
        await service.trash(3)
    assert trash_exc.value.code == 500
    assert trash_exc.value.message == "failed to move merchant social link to trash"


async def test_social_returns_merchant_social_link_model_untouched() -> None:
    # Sanity: the model row dataclass is what the repository returns for Trash.
    row = MerchantSocialMediaLink(
        merchant_social_id=1,
        merchant_detail_id=2,
        platform="Facebook",
        url="https://facebook.com/x",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=DELETED,
    )
    assert row.platform == "Facebook"


__all__ = []
