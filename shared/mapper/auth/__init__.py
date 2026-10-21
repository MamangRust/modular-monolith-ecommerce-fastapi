"""Auth response mapper."""

from __future__ import annotations

from shared.mapper.auth.mapper import (
    to_response_forgot_password,
    to_response_get_me,
    to_response_login,
    to_response_refresh_token,
    to_response_register,
    to_response_reset_password,
    to_response_verify_code,
)


class AuthResponseMapper:
    """Bundle matching the `AuthResponseMapper` interface."""

    to_response_verify_code = staticmethod(to_response_verify_code)
    to_response_forgot_password = staticmethod(to_response_forgot_password)
    to_response_reset_password = staticmethod(to_response_reset_password)
    to_response_login = staticmethod(to_response_login)
    to_response_register = staticmethod(to_response_register)
    to_response_refresh_token = staticmethod(to_response_refresh_token)
    to_response_get_me = staticmethod(to_response_get_me)


def new_auth_response_mapper() -> AuthResponseMapper:
    return AuthResponseMapper()


__all__ = [
    "AuthResponseMapper",
    "new_auth_response_mapper",
    "to_response_forgot_password",
    "to_response_get_me",
    "to_response_login",
    "to_response_refresh_token",
    "to_response_register",
    "to_response_reset_password",
    "to_response_verify_code",
]
