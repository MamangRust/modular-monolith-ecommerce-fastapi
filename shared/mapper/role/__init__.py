"""Role response mapper."""

from __future__ import annotations

from shared.mapper.role.command import (
    to_api_response_role_all,
    to_api_response_role_delete,
)
from shared.mapper.role.query import (
    map_pagination_meta,
    to_api_response_pagination_role,
    to_api_response_pagination_role_delete_at,
    to_api_response_role,
    to_api_responses_role,
)


class RoleQueryMapper:
    """Query-side mapper bundle (`RoleQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_role = staticmethod(to_api_response_role)
    to_api_responses_role = staticmethod(to_api_responses_role)
    to_api_response_pagination_role = staticmethod(to_api_response_pagination_role)
    to_api_response_pagination_role_delete_at = staticmethod(
        to_api_response_pagination_role_delete_at
    )


class RoleCommandMapper:
    """Command-side mapper bundle (`RoleCommandResponseMapper`)."""

    to_api_response_role_delete = staticmethod(to_api_response_role_delete)
    to_api_response_role_all = staticmethod(to_api_response_role_all)


class RoleResponseMapper:
    """Factory `NewRoleResponseMapper`."""

    def __init__(self) -> None:
        self._query = RoleQueryMapper()
        self._command = RoleCommandMapper()

    def query_mapper(self) -> RoleQueryMapper:
        return self._query

    def command_mapper(self) -> RoleCommandMapper:
        return self._command


def new_role_response_mapper() -> RoleResponseMapper:
    return RoleResponseMapper()


__all__ = [
    "RoleCommandMapper",
    "RoleQueryMapper",
    "RoleResponseMapper",
    "map_pagination_meta",
    "new_role_response_mapper",
    "to_api_response_pagination_role",
    "to_api_response_pagination_role_delete_at",
    "to_api_response_role",
    "to_api_response_role_all",
    "to_api_response_role_delete",
    "to_api_responses_role",
]
