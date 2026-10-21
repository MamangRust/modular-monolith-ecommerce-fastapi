"""Merchant document command service. `create` and `update_status` are transactional and enqueue an outbox email within the same commit. Resolving the owner's email must never fail the document operation, so `_publish_document_email` logs and swallows every error (missing merchant/user, marshal failure, enqueue failure). has a non-transactional fallback that sends the email straight to Kafka when no pool/tx is present; always runs with a `Database`, so that branch is unreachable and omitted. The outbox `event_key` for the repeatable status update carries a uuid suffix (the `outbox_events.event_key` is UNIQUE, 's) — see the notes."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from pkg.database.database import Database
from pkg.database.schema.merchant_document import (
    CreateMerchantDocumentRow,
    MerchantDocument,
    UpdateMerchantDocumentRow,
    UpdateMerchantDocumentStatusRow,
)
from pkg.event import marshal_email
from pkg.logger.logger import Logger
from pkg.outbox import Event, enqueue
from service.merchant.redis.interfaces import MerchantDocumentCommandCache
from service.merchant.repository.interfaces import (
    MerchantDocumentCommandRepository,
    MerchantQueryRepository,
    UserQueryRepository,
)
from service.merchant.service.emails import email_body
from shared.domain.requests.merchant import (
    CreateMerchantDocumentRequest,
    UpdateMerchantDocumentRequest,
    UpdateMerchantDocumentStatusRequest,
)
from shared.observability import Observability

EnqueueFn = Callable[[Any, Event], Awaitable[None]]

_TOPIC_DOCUMENT_CREATE = "email-service-topic-merchant-document-create"
_TOPIC_DOCUMENT_UPDATE_STATUS = "email-service-topic-merchant-document-update-status"


class MerchantDocumentCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantDocumentCommandRepository,
        merchant_query: MerchantQueryRepository,
        user_query: UserQueryRepository,
        cache: MerchantDocumentCommandCache,
        db: Database,
        logger: Logger,
        obs: Observability,
        *,
        enqueue_fn: EnqueueFn = enqueue,
    ) -> None:
        self._repo = repo
        self._merchant_query = merchant_query
        self._user_query = user_query
        self._cache = cache
        self._db = db
        self._logger = logger
        self._obs = obs
        self._enqueue = enqueue_fn

    async def create(
        self, request: CreateMerchantDocumentRequest
    ) -> CreateMerchantDocumentRow:
        with self._obs.span(
            "merchant_document.command.create", merchant_id=request.merchant_id
        ):
            async with self._db.transaction() as conn:
                res = await self._repo.create_in_tx(conn, request)
                await self._publish_document_email(
                    conn,
                    _TOPIC_DOCUMENT_CREATE,
                    "merchant-document-create",
                    "merchant_document.created",
                    res.document_id,
                    res.merchant_id,
                    "Document Uploaded - SanEdge",
                    "Your document has been uploaded successfully. Our team will "
                    "review it and notify you once its status changes.",
                )
            self._logger.info(
                "merchant document created", document_id=res.document_id
            )
            return res

    async def update(
        self, request: UpdateMerchantDocumentRequest
    ) -> UpdateMerchantDocumentRow:
        document_id = request.document_id or 0
        with self._obs.span(
            "merchant_document.command.update", document_id=document_id
        ):
            res = await self._repo.update(request)
            await self._cache.delete_cached_merchant_documents(document_id)
            self._logger.info("merchant document updated", document_id=document_id)
            return res

    async def update_status(
        self, request: UpdateMerchantDocumentStatusRequest
    ) -> UpdateMerchantDocumentStatusRow:
        document_id = request.document_id or 0
        with self._obs.span(
            "merchant_document.command.update_status", document_id=document_id
        ):
            async with self._db.transaction() as conn:
                res = await self._repo.update_status_in_tx(conn, request)
                subject, message = _document_status_email(res.status)
                await self._publish_document_email(
                    conn,
                    _TOPIC_DOCUMENT_UPDATE_STATUS,
                    "merchant-document-update-status",
                    "merchant_document.status_updated",
                    res.document_id,
                    res.merchant_id,
                    subject,
                    message,
                )
            await self._cache.delete_cached_merchant_documents(document_id)
            self._logger.info(
                "merchant document status updated", document_id=document_id
            )
            return res

    async def trash(self, document_id: int) -> MerchantDocument:
        with self._obs.span("merchant_document.command.trash", document_id=document_id):
            res = await self._repo.trash(document_id)
            await self._cache.delete_cached_merchant_documents(document_id)
            self._logger.info("merchant document trashed", document_id=document_id)
            return res

    async def restore(self, document_id: int) -> MerchantDocument:
        with self._obs.span(
            "merchant_document.command.restore", document_id=document_id
        ):
            res = await self._repo.restore(document_id)
            await self._cache.delete_cached_merchant_documents(document_id)
            self._logger.info("merchant document restored", document_id=document_id)
            return res

    async def delete_permanent(self, document_id: int) -> bool:
        with self._obs.span(
            "merchant_document.command.delete_permanent", document_id=document_id
        ):
            await self._repo.delete_permanent(document_id)
            await self._cache.delete_cached_merchant_documents(document_id)
            self._logger.info(
                "merchant document deleted permanently", document_id=document_id
            )
            return True

    async def restore_all(self) -> bool:
        # does not invalidate the cache for the bulk ops.
        with self._obs.span("merchant_document.command.restore_all"):
            await self._repo.restore_all()
            self._logger.info("all merchant documents restored")
            return True

    async def delete_all(self) -> bool:
        # does not invalidate the cache for the bulk ops.
        with self._obs.span("merchant_document.command.delete_all"):
            await self._repo.delete_all()
            self._logger.info("all merchant documents deleted permanently")
            return True

    async def _publish_document_email(
        self,
        conn: Any,
        topic: str,
        event_key_prefix: str,
        event_type: str,
        document_id: int,
        merchant_id: int,
        subject: str,
        message: str,
    ) -> None:
        """Resolve the owner's email and enqueue the email event. Every failure is logged and swallowed: email delivery must never fail the document operation, matching the `publishDocumentEmail`."""
        try:
            merchant = await self._merchant_query.find_by_id(merchant_id)
            user = await self._user_query.find_by_id(merchant.user_id)
            payload = marshal_email(
                event_type,
                user.email,
                subject,
                email_body(
                    message,
                    "Go to Portal",
                    f"https://sanedge.example.com/merchant/{merchant_id}/documents",
                ),
            )
            await self._enqueue(
                conn,
                Event(
                    event_key=f"{event_key_prefix}:{document_id}:{uuid4().hex}",
                    topic=topic,
                    key=str(document_id),
                    payload=payload,
                ),
            )
        except Exception as exc:
            self._logger.error(
                "failed to enqueue merchant document email",
                topic=topic,
                document_id=document_id,
                error=str(exc),
            )


def _document_status_email(status: str) -> tuple[str, str]:
    if status == "approved":
        return (
            "Document Approved - SanEdge",
            "Congratulations! Your document has been <b>approved</b>. Your "
            "merchant account is one step closer to activation.",
        )
    if status == "rejected":
        return (
            "Document Rejected - SanEdge",
            "We're sorry, but your document has been <b>rejected</b>. Please "
            "review the note and re-upload the corrected document.",
        )
    return (
        "Document Status Updated - SanEdge",
        "Your document status has been updated.",
    )


__all__ = ["EnqueueFn", "MerchantDocumentCommandServiceImpl"]
