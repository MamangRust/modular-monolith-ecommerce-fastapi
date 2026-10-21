"""Transaction gRPC adapter. Dead wiring: the order command service constructs this adapter but never calls it — permanent deletion of an order's transactions goes through the atomic `DeletePermanentWithChildren` CTE (which touches the `transactions` table directly), and `DeleteAll` iterates trashed orders rather than calling the transaction service's global delete. keeps the adapter (and its wiring) for; the transaction service itself is a later domain. returns the raw RPC error (no wrapping) and guards against a nil client; keeps both behaviours."""

from __future__ import annotations

from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.resilience.dependency_guard import DependencyGuard

_TIMEOUT_SECONDS = 30


class TransactionCommandAdapter:

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
    ) -> None:
        from pb.transaction import (
            transaction_command_pb2_grpc,
            transaction_common_pb2,
        )

        self._common = transaction_common_pb2
        self._command = (
            transaction_command_pb2_grpc.TransactionCommandServiceStub(channel)
        )
        self._guard = guard

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def delete_by_order_id_permanent(self, order_id: int) -> bool:
        async def invoke() -> Any:
            return await self._command.DeleteTransactionByOrderPermanent(
                self._common.FindByIdTransactionRequest(id=order_id),
                timeout=_TIMEOUT_SECONDS,
            )

        await guard_call(self._guard, invoke)
        return True

    async def delete_all(self) -> bool:
        from google.protobuf.empty_pb2 import Empty

        async def invoke() -> Any:
            return await self._command.DeleteAllTransactionPermanent(
                Empty(), timeout=_TIMEOUT_SECONDS
            )

        resp = await guard_call(self._guard, invoke)
        return resp.status == "success"


__all__ = ["TransactionCommandAdapter"]
