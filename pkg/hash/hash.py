"""Password hashing."""

from __future__ import annotations

import bcrypt


class InvalidCredentialsError(Exception):
    pass


class Hasher:
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

    def compare_password(self, hashed: str, password: str) -> None:
        try:
            if not bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8")):
                raise InvalidCredentialsError("invalid credentials")
        except ValueError:
            # Malformed hash stored in DB — treat as credential failure,
            # never leak the parse error.
            raise InvalidCredentialsError("invalid credentials") from None
