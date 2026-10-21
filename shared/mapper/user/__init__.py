"""User response mapper."""

from __future__ import annotations

from shared.mapper.user.command import (
    to_api_response_user_all,
    to_api_response_user_delete,
    to_api_response_user_delete_at,
)
from shared.mapper.user.query import (
    map_pagination_meta,
    to_api_response_pagination_user,
    to_api_response_pagination_user_delete_at,
    to_api_response_user,
    to_api_responses_user,
)


class UserQueryMapper:
    """Query-side mapper bundle (`UserQueryResponseMapper`)."""

    map_pagination_meta = staticmethod(map_pagination_meta)
    to_api_response_user = staticmethod(to_api_response_user)
    to_api_responses_user = staticmethod(to_api_responses_user)
    to_api_response_pagination_user = staticmethod(to_api_response_pagination_user)
    to_api_response_pagination_user_delete_at = staticmethod(
        to_api_response_pagination_user_delete_at
    )


class UserCommandMapper:
    """Command-side mapper bundle (`UserCommandResponseMapper`)."""

    to_api_response_user = staticmethod(to_api_response_user)
    to_api_response_user_delete_at = staticmethod(to_api_response_user_delete_at)
    to_api_response_user_delete = staticmethod(to_api_response_user_delete)
    to_api_response_user_all = staticmethod(to_api_response_user_all)


class UserResponseMapper:
    """Factory `NewUserResponseMapper`."""

    def __init__(self) -> None:
        self._query = UserQueryMapper()
        self._command = UserCommandMapper()

    def query_mapper(self) -> UserQueryMapper:
        return self._query

    def command_mapper(self) -> UserCommandMapper:
        return self._command


def new_user_response_mapper() -> UserResponseMapper:
    return UserResponseMapper()


__all__ = [
    "UserCommandMapper",
    "UserQueryMapper",
    "UserResponseMapper",
    "map_pagination_meta",
    "new_user_response_mapper",
    "to_api_response_pagination_user",
    "to_api_response_pagination_user_delete_at",
    "to_api_response_user",
    "to_api_response_user_all",
    "to_api_response_user_delete",
    "to_api_response_user_delete_at",
    "to_api_responses_user",
]
