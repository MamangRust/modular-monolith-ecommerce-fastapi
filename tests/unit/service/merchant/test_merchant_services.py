"""Unit tests for merchant + merchant_document services (no DB/Redis). Covers the cache-first query services, the transactional command services (write + outbox event committed together), the direct Kafka status event, the email resolution rules, and cache-invalidation: - merchant/document single mutations evict the by-id key; the bulk `restore_all`/`delete_all` ops deliberately do NOT (behaviour); - `create` does not evict either; - document email failures are swallowed (never fail the document op)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from pkg.database.schema.merchant import (
    CreateMerchantRow,
    GetMerchantByIDRow,
    GetMerchantsActiveRow,
    GetMerchantsRow,
    GetUserByIDRow,
    Merchant,
)
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    GetActiveMerchantDocumentsRow,
    GetMerchantDocumentRow,
    GetMerchantDocumentsRow,
    MerchantDocument,
)
from pkg.logger.logger import Logger
from service.merchant.service.merchant_command_service import (
    MerchantCommandServiceImpl,
)
from service.merchant.service.merchant_document_command_service import (
    MerchantDocumentCommandServiceImpl,
)
from service.merchant.service.merchant_document_query_service import (
    MerchantDocumentQueryServiceImpl,
)
from service.merchant.service.merchant_query_service import MerchantQueryServiceImpl
from shared.domain.requests.merchant import (
    CreateMerchantDocumentRequest,
    CreateMerchantRequest,
    UpdateMerchantDocumentRequest,
    UpdateMerchantDocumentStatusRequest,
    UpdateMerchantRequest,
    UpdateMerchantStatusRequest,
)
from shared.errors import AppError
from shared.observability import Observability

CREATED = datetime(2026, 1, 2, 3, 4, 5)
UPDATED = datetime(2026, 1, 3, 4, 5, 6)
DELETED = datetime(2026, 2, 1, 5, 6, 7)


# ---- shared fakes ----


class FakeTransaction:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    async def __aenter__(self) -> Any:
        return self._conn

    async def __aexit__(self, *exc: Any) -> bool:
        return False


class FakeDB:
    def __init__(self) -> None:
        self.conn = object()
        self.transactions = 0

    def transaction(self) -> FakeTransaction:
        self.transactions += 1
        return FakeTransaction(self.conn)


class FakeEnqueue:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def __call__(self, conn: Any, event: Any) -> None:
        self.events.append(event)


class FakeKafka:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    async def send_message(self, topic: str, key: str, value: str) -> None:
        self.sent.append((topic, key, value))


class FakeUserRepo:
    async def find_by_id(self, user_id: int) -> GetUserByIDRow:
        return GetUserByIDRow(
            user_id=user_id,
            firstname="T",
            lastname="U",
            email="owner@example.com",
            password="",
            created_at=CREATED,
            updated_at=UPDATED,
        )


class MissingUserRepo:
    async def find_by_id(self, user_id: int) -> GetUserByIDRow:
        raise AppError("NOT_FOUND", 404, "user not found")


def _logger() -> Logger:
    return Logger("test", "error")


def _obs() -> Observability:
    return Observability("test", _logger())


# ---- merchant query service ----


def _merchant_row(merchant_id: int = 1, total: int = 1) -> GetMerchantsRow:
    return GetMerchantsRow(
        merchant_id=merchant_id,
        user_id=10,
        name="N",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _merchant_active_row() -> GetMerchantsActiveRow:
    return GetMerchantsActiveRow(
        merchant_id=1,
        user_id=10,
        name="N",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=1,
    )


def _merchant_by_id(merchant_id: int = 1) -> GetMerchantByIDRow:
    return GetMerchantByIDRow(
        merchant_id=merchant_id,
        user_id=10,
        name="N",
        description=None,
        address=None,
        contact_email=None,
        contact_phone=None,
        status="active",
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeMerchantQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append(f"find_all:{search}:{page}:{page_size}")
        return [_merchant_row(total=1)]

    async def find_active(self, search, page, page_size):
        self.calls.append("find_active")
        return [_merchant_active_row()]

    async def find_trashed(self, search, page, page_size):
        self.calls.append("find_trashed")
        return [_merchant_active_row()]

    async def find_by_id(self, merchant_id):
        self.calls.append(f"find_by_id:{merchant_id}")
        return _merchant_by_id(merchant_id)


class FakeMerchantQueryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.writes: list[str] = []

    async def get_merchants(self, page, page_size, search):
        return self.store.get(f"all:{page}:{page_size}:{search}")

    async def set_merchants(self, page, page_size, search, rows, total):
        self.writes.append(f"all:{page}:{page_size}:{search}")
        self.store[f"all:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_active(self, page, page_size, search):
        return self.store.get(f"active:{page}:{page_size}:{search}")

    async def set_merchant_active(self, page, page_size, search, rows, total):
        self.store[f"active:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant_trashed(self, page, page_size, search):
        return self.store.get(f"trashed:{page}:{page_size}:{search}")

    async def set_merchant_trashed(self, page, page_size, search, rows, total):
        self.store[f"trashed:{page}:{page_size}:{search}"] = (rows, total)

    async def get_merchant(self, merchant_id):
        return self.store.get(f"id:{merchant_id}")

    async def set_merchant(self, row):
        self.writes.append(f"id:{row.merchant_id}")
        self.store[f"id:{row.merchant_id}"] = row


def _merchant_query_service(
    repo: FakeMerchantQueryRepo, cache: FakeMerchantQueryCache
) -> MerchantQueryServiceImpl:
    return MerchantQueryServiceImpl(repo, cache, _logger(), _obs())


async def test_merchant_find_all_caches_and_serves_cache_first() -> None:
    repo, cache = FakeMerchantQueryRepo(), FakeMerchantQueryCache()
    service = _merchant_query_service(repo, cache)

    rows, total = await service.find_all("", 1, 10)
    assert total == 1
    assert cache.writes == ["all:1:10:"]
    repo.calls.clear()

    cached_rows, _ = await service.find_all("", 1, 10)
    assert repo.calls == []
    assert cached_rows[0].merchant_id == rows[0].merchant_id


async def test_merchant_find_by_id_caches() -> None:
    repo, cache = FakeMerchantQueryRepo(), FakeMerchantQueryCache()
    service = _merchant_query_service(repo, cache)

    await service.find_by_id(5)
    assert repo.calls == ["find_by_id:5"]
    assert cache.writes == ["id:5"]


async def test_merchant_query_propagates_repo_error() -> None:
    class FailingRepo(FakeMerchantQueryRepo):
        async def find_all(self, search, page, page_size):
            raise AppError("NOT_FOUND", 404, "failed to find all merchants")

    service = _merchant_query_service(FailingRepo(), FakeMerchantQueryCache())
    with pytest.raises(AppError) as excinfo:
        await service.find_all("", 1, 10)
    assert excinfo.value.code == 404


# ---- merchant command service ----


class FakeMerchantCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        return await self.create_in_tx(None, request)

    async def create_in_tx(self, conn, request):
        self.calls.append(f"create_in_tx:{request.user_id}")
        return CreateMerchantRow(
            merchant_id=9,
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            address=request.address,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            status=request.status,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.merchant_id}")
        return _merchant_by_id(request.merchant_id or 1)

    async def update_status(self, request):
        return await self.update_status_in_tx(None, request)

    async def update_status_in_tx(self, conn, request):
        self.calls.append(f"update_status_in_tx:{request.merchant_id}")
        return _merchant_by_id(request.merchant_id or 1)

    async def trash(self, merchant_id):
        self.calls.append(f"trash:{merchant_id}")
        return Merchant(
            merchant_id=merchant_id,
            user_id=10,
            name="N",
            description=None,
            address=None,
            contact_email=None,
            contact_phone=None,
            status="active",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, merchant_id):
        self.calls.append(f"restore:{merchant_id}")
        return Merchant(
            merchant_id=merchant_id,
            user_id=10,
            name="N",
            description=None,
            address=None,
            contact_email=None,
            contact_phone=None,
            status="active",
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, merchant_id):
        self.calls.append(f"delete:{merchant_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


class FakeMerchantCommandCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []
        self.invalidations = 0

    async def delete_cached_merchant(self, merchant_id: int) -> int:
        self.evicted.append(merchant_id)
        return 1

    async def invalidate_merchant_cache(self) -> int:
        self.invalidations += 1
        return 1


def _merchant_command_service(
    repo: FakeMerchantCommandRepo,
    cache: FakeMerchantCommandCache,
    *,
    user_repo: Any | None = None,
    query_repo: FakeMerchantQueryRepo | None = None,
    kafka: Any | None = None,
    enqueue: FakeEnqueue | None = None,
    db: FakeDB | None = None,
) -> MerchantCommandServiceImpl:
    return MerchantCommandServiceImpl(
        repo,
        query_repo or FakeMerchantQueryRepo(),
        user_repo or FakeUserRepo(),
        cache,
        db or FakeDB(),  # type: ignore[arg-type]
        kafka,
        _logger(),
        _obs(),
        enqueue_fn=enqueue or FakeEnqueue(),
    )


async def test_merchant_create_commits_write_and_outbox_together() -> None:
    repo, cache, enqueue, db = (
        FakeMerchantCommandRepo(),
        FakeMerchantCommandCache(),
        FakeEnqueue(),
        FakeDB(),
    )
    service = _merchant_command_service(repo, cache, enqueue=enqueue, db=db)

    row = await service.create(
        CreateMerchantRequest(
            user_id=10,
            name="N",
            description="d",
            address="a",
            contact_email="e@f.com",
            contact_phone="0812",
            status="active",
        )
    )

    assert row.merchant_id == 9
    assert db.transactions == 1
    assert repo.calls == ["create_in_tx:10"]
    assert len(enqueue.events) == 1
    event = enqueue.events[0]
    assert event.event_key == "merchant-create:9"
    assert event.topic == "email-service-topic-merchant-create"
    # create does not evict the cache.
    assert cache.evicted == []


async def test_merchant_create_propagates_user_lookup_error() -> None:
    service = _merchant_command_service(
        FakeMerchantCommandRepo(), FakeMerchantCommandCache(), user_repo=MissingUserRepo()
    )
    with pytest.raises(AppError) as excinfo:
        await service.create(
            CreateMerchantRequest(
                user_id=999,
                name="N",
                description="d",
                address="a",
                contact_email="e@f.com",
                contact_phone="0812",
                status="active",
            )
        )
    assert excinfo.value.code == 404


async def test_merchant_update_evicts_cache() -> None:
    repo, cache = FakeMerchantCommandRepo(), FakeMerchantCommandCache()
    service = _merchant_command_service(repo, cache)
    await service.update(
        UpdateMerchantRequest(
            merchant_id=4,
            user_id=10,
            name="N",
            description="d",
            address="a",
            contact_email="e@f.com",
            contact_phone="0812",
            status="active",
        )
    )
    assert cache.evicted == [4]


async def test_merchant_update_status_active_sends_email_and_kafka() -> None:
    repo, cache, enqueue, kafka, db = (
        FakeMerchantCommandRepo(),
        FakeMerchantCommandCache(),
        FakeEnqueue(),
        FakeKafka(),
        FakeDB(),
    )
    service = _merchant_command_service(
        repo, cache, enqueue=enqueue, kafka=kafka, db=db
    )

    await service.update_status(
        UpdateMerchantStatusRequest(merchant_id=4, status="active")
    )

    assert db.transactions == 1
    assert len(enqueue.events) == 1
    event = enqueue.events[0]
    assert event.event_key.startswith("merchant-update-status:4:")
    assert event.topic == "email-service-topic-merchant-update-status"
    assert len(kafka.sent) == 1
    assert kafka.sent[0][0] == "transaction-service-topic-merchant-status-event"
    assert cache.evicted == [4]


async def test_merchant_update_status_unknown_status_skips_email_and_kafka() -> None:
    repo, cache, enqueue, kafka = (
        FakeMerchantCommandRepo(),
        FakeMerchantCommandCache(),
        FakeEnqueue(),
        FakeKafka(),
    )
    service = _merchant_command_service(repo, cache, enqueue=enqueue, kafka=kafka)

    await service.update_status(
        UpdateMerchantStatusRequest(merchant_id=4, status="suspended")
    )

    assert enqueue.events == []
    assert kafka.sent == []
    # Cache is still evicted on the mutation.
    assert cache.evicted == [4]


async def test_merchant_single_mutations_evict_bulk_do_not() -> None:
    repo, cache = FakeMerchantCommandRepo(), FakeMerchantCommandCache()
    service = _merchant_command_service(repo, cache)

    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    assert cache.evicted == [2, 2, 2]

    cache.evicted.clear()
    await service.restore_all()
    await service.delete_all()
    assert cache.evicted == []


# ---- document query service ----


def _doc_row(document_id: int = 1, total: int = 1) -> GetMerchantDocumentsRow:
    return GetMerchantDocumentsRow(
        document_id=document_id,
        merchant_id=10,
        document_type="NIB",
        document_url="u",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        total_count=total,
    )


def _doc_active_row() -> GetActiveMerchantDocumentsRow:
    return GetActiveMerchantDocumentsRow(
        document_id=1,
        merchant_id=10,
        document_type="NIB",
        document_url="u",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
        deleted_at=None,
        total_count=1,
    )


def _doc_by_id(document_id: int = 1) -> GetMerchantDocumentRow:
    return GetMerchantDocumentRow(
        document_id=document_id,
        merchant_id=10,
        document_type="NIB",
        document_url="u",
        status="pending",
        note=None,
        uploaded_at=CREATED,
        created_at=CREATED,
        updated_at=UPDATED,
    )


class FakeDocumentQueryRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def find_all(self, search, page, page_size):
        self.calls.append("find_all")
        return [_doc_row()], 1

    async def find_active(self, search, page, page_size):
        self.calls.append("find_active")
        return [_doc_active_row()], 1

    async def find_trashed(self, search, page, page_size):
        self.calls.append("find_trashed")
        return [_doc_active_row()], 1

    async def find_by_id(self, document_id):
        self.calls.append(f"find_by_id:{document_id}")
        return _doc_by_id(document_id)


class FakeDocumentQueryCache:
    def __init__(self) -> None:
        self.reads = 0

    async def get_merchant_documents(self, page, page_size, search):
        self.reads += 1
        return None

    async def set_merchant_documents(self, page, page_size, search, rows, total):
        return None

    async def get_merchant_documents_active(self, page, page_size, search):
        return None

    async def set_merchant_documents_active(
        self, page, page_size, search, rows, total
    ):
        return None

    async def get_merchant_documents_trashed(self, page, page_size, search):
        return None

    async def set_merchant_documents_trashed(
        self, page, page_size, search, rows, total
    ):
        return None

    async def get_merchant_document(self, document_id):
        return None

    async def set_merchant_document(self, row):
        return None


async def test_document_query_hits_repo_and_ignores_cache() -> None:
    repo, cache = FakeDocumentQueryRepo(), FakeDocumentQueryCache()
    service = MerchantDocumentQueryServiceImpl(repo, cache, _logger(), _obs())

    rows, total = await service.find_all("", 1, 10)
    await service.find_by_id(3)

    assert total == 1
    assert repo.calls == ["find_all", "find_by_id:3"]
    assert cache.reads == 0


# ---- document command service ----


class FakeDocumentCommandRepo:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def create(self, request):
        return await self.create_in_tx(None, request)

    async def create_in_tx(self, conn, request):
        self.calls.append(f"create_in_tx:{request.merchant_id}")
        return CreateMerchantDocumentRow(
            document_id=9,
            merchant_id=request.merchant_id,
            document_type=request.document_type,
            document_url=request.document_url,
            status="pending",
            note=None,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
        )

    async def update(self, request):
        self.calls.append(f"update:{request.document_id}")
        return _doc_by_id(request.document_id or 1)

    async def update_status(self, request):
        return await self.update_status_in_tx(None, request)

    async def update_status_in_tx(self, conn, request):
        self.calls.append(f"update_status_in_tx:{request.document_id}")
        return _doc_by_id(request.document_id or 1)

    async def trash(self, document_id):
        self.calls.append(f"trash:{document_id}")
        return MerchantDocument(
            document_id=document_id,
            merchant_id=10,
            document_type="NIB",
            document_url="u",
            status="pending",
            note=None,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=DELETED,
        )

    async def restore(self, document_id):
        self.calls.append(f"restore:{document_id}")
        return MerchantDocument(
            document_id=document_id,
            merchant_id=10,
            document_type="NIB",
            document_url="u",
            status="pending",
            note=None,
            uploaded_at=CREATED,
            created_at=CREATED,
            updated_at=UPDATED,
            deleted_at=None,
        )

    async def delete_permanent(self, document_id):
        self.calls.append(f"delete:{document_id}")
        return True

    async def restore_all(self):
        self.calls.append("restore_all")
        return True

    async def delete_all(self):
        self.calls.append("delete_all")
        return True


class FakeDocumentCommandCache:
    def __init__(self) -> None:
        self.evicted: list[int] = []

    async def delete_cached_merchant_documents(self, document_id: int) -> int:
        self.evicted.append(document_id)
        return 1


def _document_command_service(
    repo: FakeDocumentCommandRepo,
    cache: FakeDocumentCommandCache,
    *,
    merchant_query: Any | None = None,
    user_query: Any | None = None,
    enqueue: FakeEnqueue | None = None,
    db: FakeDB | None = None,
) -> MerchantDocumentCommandServiceImpl:
    return MerchantDocumentCommandServiceImpl(
        repo,
        merchant_query or FakeMerchantQueryRepo(),
        user_query or FakeUserRepo(),
        cache,
        db or FakeDB(),  # type: ignore[arg-type]
        _logger(),
        _obs(),
        enqueue_fn=enqueue or FakeEnqueue(),
    )


async def test_document_create_commits_write_and_email_together() -> None:
    repo, cache, enqueue, db = (
        FakeDocumentCommandRepo(),
        FakeDocumentCommandCache(),
        FakeEnqueue(),
        FakeDB(),
    )
    service = _document_command_service(repo, cache, enqueue=enqueue, db=db)

    row = await service.create(
        CreateMerchantDocumentRequest(
            merchant_id=10, document_type="NIB", document_url="uploads/a.pdf"
        )
    )

    assert row.document_id == 9
    assert db.transactions == 1
    assert len(enqueue.events) == 1
    event = enqueue.events[0]
    assert event.event_key.startswith("merchant-document-create:9:")
    assert event.topic == "email-service-topic-merchant-document-create"
    assert cache.evicted == []


async def test_document_create_swallows_email_lookup_failure() -> None:
    enqueue = FakeEnqueue()
    service = _document_command_service(
        FakeDocumentCommandRepo(),
        FakeDocumentCommandCache(),
        user_query=MissingUserRepo(),
        enqueue=enqueue,
    )

    row = await service.create(
        CreateMerchantDocumentRequest(
            merchant_id=10, document_type="NIB", document_url="uploads/a.pdf"
        )
    )

    # The document is created even though the owner lookup failed.
    assert row.document_id == 9
    assert enqueue.events == []


async def test_document_update_status_evicts_cache_and_emails() -> None:
    repo, cache, enqueue = (
        FakeDocumentCommandRepo(),
        FakeDocumentCommandCache(),
        FakeEnqueue(),
    )
    service = _document_command_service(repo, cache, enqueue=enqueue)

    await service.update_status(
        UpdateMerchantDocumentStatusRequest(
            document_id=4, merchant_id=10, status="approved", note="ok"
        )
    )

    assert len(enqueue.events) == 1
    assert enqueue.events[0].topic == (
        "email-service-topic-merchant-document-update-status"
    )
    assert cache.evicted == [4]


async def test_document_single_mutations_evict_bulk_do_not() -> None:
    repo, cache = FakeDocumentCommandRepo(), FakeDocumentCommandCache()
    service = _document_command_service(repo, cache)

    await service.update(
        UpdateMerchantDocumentRequest(
            document_id=4,
            merchant_id=10,
            document_type="NIB",
            document_url="u",
            status="pending",
            note="ok",
        )
    )
    await service.trash(2)
    await service.restore(2)
    await service.delete_permanent(2)
    assert cache.evicted == [4, 2, 2, 2]

    cache.evicted.clear()
    await service.restore_all()
    await service.delete_all()
    assert cache.evicted == []


__all__ = []
