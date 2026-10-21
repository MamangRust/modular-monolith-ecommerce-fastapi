"""Merchant command service. `create` and `update_status` are transactional: the write and its outbox event commit together (`async with db.transaction`), then the outbox relay publishes the email. `update_status` additionally emits a *direct* Kafka status event for the transaction service (`transaction-service-topic-merchant-status-event`), which is not an outbox event and is sent after the commit. Email is only produced for a create, and for a status of active/inactive/ rejected; other statuses build no subject and therefore no email. The outbox `event_key` must be unique (the `outbox_events` has a UNIQUE constraint does not), so repeatable events (status updates) append a uuid suffix — see the."""

from __future__ import annotations

import json
import time
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from pkg.database.database import Database
from pkg.database.schema.merchant import (
    CreateMerchantRow,
    Merchant,
    UpdateMerchantRow,
    UpdateMerchantStatusRow,
)
from pkg.event import marshal_email
from pkg.kafka.kafka import Kafka
from pkg.logger.logger import Logger
from pkg.outbox import Event, enqueue
from service.merchant.redis.interfaces import MerchantCommandCache
from service.merchant.repository.interfaces import (
    MerchantCommandRepository,
    MerchantQueryRepository,
    UserQueryRepository,
)
from service.merchant.service.emails import email_body
from shared.domain.requests.merchant import (
    CreateMerchantRequest,
    UpdateMerchantRequest,
    UpdateMerchantStatusRequest,
)
from shared.observability import Observability

EnqueueFn = Callable[[Any, Event], Awaitable[None]]

_TOPIC_MERCHANT_CREATE = "email-service-topic-merchant-create"
_TOPIC_MERCHANT_UPDATE_STATUS = "email-service-topic-merchant-update-status"
_TOPIC_MERCHANT_STATUS_EVENT = "transaction-service-topic-merchant-status-event"


class MerchantCommandServiceImpl:
    def __init__(
        self,
        repo: MerchantCommandRepository,
        query_repo: MerchantQueryRepository,
        user_repo: UserQueryRepository,
        cache: MerchantCommandCache,
        db: Database,
        kafka: Kafka | None,
        logger: Logger,
        obs: Observability,
        *,
        enqueue_fn: EnqueueFn = enqueue,
    ) -> None:
        self._repo = repo
        self._query_repo = query_repo
        self._user_repo = user_repo
        self._cache = cache
        self._db = db
        self._kafka = kafka
        self._logger = logger
        self._obs = obs
        self._enqueue = enqueue_fn

    async def create(self, request: CreateMerchantRequest) -> CreateMerchantRow:
        with self._obs.span("merchant.command.create", user_id=request.user_id):
            user = await self._user_repo.find_by_id(request.user_id)
            payload = marshal_email(
                "merchant.created",
                user.email,
                "Initial Verification - SanEdge",
                email_body(
                    "Your merchant account has been created successfully. To "
                    "continue, please upload the required documents for "
                    "verification. Once completed, our team will review and "
                    "activate your account.",
                    "Upload Documents",
                    f"https://sanedge.example.com/merchant/{user.user_id}/documents",
                ),
            )
            async with self._db.transaction() as conn:
                res = await self._repo.create_in_tx(conn, request)
                await self._enqueue(
                    conn,
                    Event(
                        event_key=f"merchant-create:{res.merchant_id}",
                        topic=_TOPIC_MERCHANT_CREATE,
                        key=str(res.merchant_id),
                        payload=payload,
                    ),
                )
            self._logger.info("merchant created", merchant_id=res.merchant_id)
            return res

    async def update(self, request: UpdateMerchantRequest) -> UpdateMerchantRow:
        merchant_id = request.merchant_id or 0
        with self._obs.span("merchant.command.update", merchant_id=merchant_id):
            res = await self._repo.update(request)
            await self._cache.delete_cached_merchant(merchant_id)
            self._logger.info("merchant updated", merchant_id=merchant_id)
            return res

    async def update_status(
        self, request: UpdateMerchantStatusRequest
    ) -> UpdateMerchantStatusRow:
        merchant_id = request.merchant_id or 0
        with self._obs.span(
            "merchant.command.update_status", merchant_id=merchant_id
        ):
            merchant = await self._query_repo.find_by_id(merchant_id)
            user = await self._user_repo.find_by_id(merchant.user_id)

            subject, message = _status_email(request.status)
            link = f"https://sanedge.example.com/merchant/{merchant_id}/dashboard"

            async with self._db.transaction() as conn:
                res = await self._repo.update_status_in_tx(conn, request)
                if subject != "":
                    payload = marshal_email(
                        "merchant.status_updated",
                        user.email,
                        subject,
                        email_body(message, "Go to Portal", link),
                    )
                    await self._enqueue(
                        conn,
                        Event(
                            event_key=(
                                f"merchant-update-status:{res.merchant_id}:"
                                f"{uuid4().hex}"
                            ),
                            topic=_TOPIC_MERCHANT_UPDATE_STATUS,
                            key=str(res.merchant_id),
                            payload=payload,
                        ),
                    )

            if self._kafka is not None and subject != "":
                await self._publish_status_event(res.merchant_id, request.status)

            await self._cache.delete_cached_merchant(merchant_id)
            self._logger.info("merchant status updated", merchant_id=merchant_id)
            return res

    async def trash(self, merchant_id: int) -> Merchant:
        with self._obs.span("merchant.command.trash", merchant_id=merchant_id):
            res = await self._repo.trash(merchant_id)
            await self._cache.delete_cached_merchant(merchant_id)
            self._logger.info("merchant trashed", merchant_id=merchant_id)
            return res

    async def restore(self, merchant_id: int) -> Merchant:
        with self._obs.span("merchant.command.restore", merchant_id=merchant_id):
            res = await self._repo.restore(merchant_id)
            await self._cache.delete_cached_merchant(merchant_id)
            self._logger.info("merchant restored", merchant_id=merchant_id)
            return res

    async def delete_permanent(self, merchant_id: int) -> bool:
        with self._obs.span(
            "merchant.command.delete_permanent", merchant_id=merchant_id
        ):
            await self._repo.delete_permanent(merchant_id)
            await self._cache.delete_cached_merchant(merchant_id)
            self._logger.info("merchant deleted permanently", merchant_id=merchant_id)
            return True

    async def restore_all(self) -> bool:
        # merchant command service does not invalidate the cache here.
        with self._obs.span("merchant.command.restore_all"):
            await self._repo.restore_all()
            self._logger.info("all merchants restored")
            return True

    async def delete_all(self) -> bool:
        # merchant command service does not invalidate the cache here.
        with self._obs.span("merchant.command.delete_all"):
            await self._repo.delete_all()
            self._logger.info("all merchants deleted permanently")
            return True

    async def _publish_status_event(self, merchant_id: int, status: str) -> None:
        assert self._kafka is not None
        event = json.dumps(
            {
                "merchantId": merchant_id,
                "status": status,
                "timestamp": int(time.time() * 1000),
            }
        )
        try:
            await self._kafka.send_message(
                _TOPIC_MERCHANT_STATUS_EVENT, str(merchant_id), event
            )
        except Exception as exc:
            self._logger.error(
                "failed to publish merchant status event",
                merchant_id=merchant_id,
                error=str(exc),
            )


def _status_email(status: str) -> tuple[str, str]:
    """Return (subject, message); an empty subject means no email is sent."""
    if status == "active":
        return (
            "Your Merchant Account is Now Active",
            "Congratulations! Your merchant account has been verified and is now "
            "<b>active</b>. You can now fully access all features in the SanEdge "
            "Merchant Portal.",
        )
    if status == "inactive":
        return (
            "Merchant Account Set to Inactive",
            "Your merchant account status has been set to <b>inactive</b>. "
            "Please contact support if you believe this is a mistake.",
        )
    if status == "rejected":
        return (
            "Merchant Account Rejected",
            "We're sorry to inform you that your merchant account has been "
            "<b>rejected</b>. Please contact support or review your submissions.",
        )
    return "", ""


__all__ = ["EnqueueFn", "MerchantCommandServiceImpl"]
