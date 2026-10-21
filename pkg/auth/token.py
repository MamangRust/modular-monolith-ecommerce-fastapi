"""JWT token manager. - `generate_token(user_id, audience)` sets the JWT audience claim to the caller-supplied value ("access" for login tokens, "refresh" for refresh tokens). - `validate_token` returns the subject string and does NOT enforce the audience: the gateway middleware likewise only checks the signature and expiry. Enforcing an audience here would reject the login tokens this same module issues."""

from __future__ import annotations

import time

import jwt


class TokenExpiredError(Exception):
    pass


class TokenManager:
    def __init__(self, secret_key: str) -> None:
        if not secret_key:
            raise ValueError("empty secret key")
        self._secret = secret_key

    def generate_token(self, user_id: int, audience: str) -> str:
        now = int(time.time())
        token = jwt.encode(
            {
                "sub": str(user_id),
                "aud": audience,
                "iat": now,
                "exp": now + 12 * 3600,
            },
            self._secret,
            algorithm="HS256",
        )
        return token

    def validate_token(self, token: str) -> str:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError("token expired") from exc
        return str(claims.get("sub", ""))


def new_manager(secret_key: str) -> TokenManager:
    return TokenManager(secret_key)
