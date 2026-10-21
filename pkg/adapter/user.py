"""User gRPC adapter. Consumers that must resolve a user remotely (card, merchant) call the user service through this read-only adapter instead of touching the users table. Maps proto `UserResponse` onto the local `db.GetUserByIDRow` shape. split single `db.GetUserByIDRow` into per-domain copies (`schema.user` / `schema.merchant`), so the adapter takes a `row_cls` — card uses the default, merchant passes its own. The password column is not on the wire and stays empty; every current consumer discards the row (existence check),."""

from __future__ import annotations

from typing import Any

import grpc.aio as grpc_aio

from pkg.adapter.guard import call as guard_call
from pkg.database.schema.user import GetUserByIDRow
from pkg.resilience.dependency_guard import DependencyGuard
from shared.errors import err_user_not_found_repo

_TIMEOUT_SECONDS = 30


def _parse_rfc3339(value: str) -> Any:
    """Mirror parseTime: an empty/invalid string yields an unset time."""
    from datetime import datetime

    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class UserQueryAdapter:
    """NewQueryAdapter: remote user lookups by id."""

    def __init__(
        self,
        channel: grpc_aio.Channel,
        *,
        guard: DependencyGuard | None = None,
        row_cls: Any = None,
    ) -> None:
        from pb.user import user_common_pb2, user_query_pb2_grpc

        self._pb2 = user_common_pb2  # FindByIdUserRequest lives in user.proto
        self._query = user_query_pb2_grpc.UserQueryServiceStub(channel)
        self._guard = guard
        self._row_cls: Any = row_cls or GetUserByIDRow

    def set_guard(self, guard: DependencyGuard | None) -> None:
        """Implement adapter.GuardSetter."""
        self._guard = guard

    async def find_by_id(self, user_id: int) -> Any:
        async def invoke() -> Any:
            return await self._query.FindById(
                self._pb2.FindByIdUserRequest(id=user_id),
                timeout=_TIMEOUT_SECONDS,
            )

        try:
            resp = await guard_call(self._guard, invoke)
        except Exception as exc:
            raise err_user_not_found_repo.with_internal(exc) from exc
        if not resp.HasField("data"):
            raise err_user_not_found_repo

        data = resp.data
        return self._row_cls(
            user_id=data.id,
            firstname=data.firstname,
            lastname=data.lastname,
            email=data.email,
            password="",
            created_at=_parse_rfc3339(data.created_at),
            updated_at=_parse_rfc3339(data.updated_at),
        )


__all__ = ["UserQueryAdapter"]
