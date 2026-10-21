"""Auth cache keys and TTLs.

Keys and durations Matches the expected `mencache` package verbatim."""

from __future__ import annotations

# Login / lockout.
AUTH_LOGIN_KEY = "auth:login:%s"
AUTH_FAILED_LOGIN_KEY = "auth:login:failed:%s"
AUTH_ACCOUNT_LOCKED_KEY = "auth:login:locked:%s"

MAX_FAILED_ATTEMPTS = 5
FAILED_LOGIN_TTL = 3600  # 1 hour
LOCKOUT_TTL = 900  # 15 minutes
LOGIN_TTL = 300  # 5 minutes

# Identity.
IDENTITY_REFRESH_TOKEN_KEY = "identity:refresh_token:%s"
IDENTITY_USER_INFO_KEY = "identity:user_info:%s"
USER_INFO_TTL = 300  # 5 minutes
REFRESH_TOKEN_TTL = 86400  # 24 hours

# Password reset / verification.
PASSWORD_RESET_TOKEN_KEY = "password_reset:token:%s"
REGISTER_VERIFY_CODE_KEY = "register:verify_code:%s"
RESET_TOKEN_TTL = 300  # 5 minutes
VERIFY_CODE_TTL = 900  # 15 minutes


def auth_login_key(email: str) -> str:
    return AUTH_LOGIN_KEY % email


def auth_failed_login_key(email: str) -> str:
    return AUTH_FAILED_LOGIN_KEY % email


def auth_account_locked_key(email: str) -> str:
    return AUTH_ACCOUNT_LOCKED_KEY % email


def identity_refresh_token_key(token: str) -> str:
    return IDENTITY_REFRESH_TOKEN_KEY % token


def identity_user_info_key(user_id: str | int) -> str:
    return IDENTITY_USER_INFO_KEY % user_id


def password_reset_token_key(token: str) -> str:
    return PASSWORD_RESET_TOKEN_KEY % token


def register_verify_code_key(email: str) -> str:
    return REGISTER_VERIFY_CODE_KEY % email


__all__ = [
    "AUTH_ACCOUNT_LOCKED_KEY",
    "AUTH_FAILED_LOGIN_KEY",
    "AUTH_LOGIN_KEY",
    "FAILED_LOGIN_TTL",
    "IDENTITY_REFRESH_TOKEN_KEY",
    "IDENTITY_USER_INFO_KEY",
    "LOCKOUT_TTL",
    "LOGIN_TTL",
    "MAX_FAILED_ATTEMPTS",
    "PASSWORD_RESET_TOKEN_KEY",
    "REGISTER_VERIFY_CODE_KEY",
    "REFRESH_TOKEN_TTL",
    "RESET_TOKEN_TTL",
    "USER_INFO_TTL",
    "VERIFY_CODE_TTL",
    "auth_account_locked_key",
    "auth_failed_login_key",
    "auth_login_key",
    "identity_refresh_token_key",
    "identity_user_info_key",
    "password_reset_token_key",
    "register_verify_code_key",
]
