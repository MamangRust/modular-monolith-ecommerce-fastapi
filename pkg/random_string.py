"""Random alphanumeric string generation. Used for email verification codes and password reset tokens. uses `crypto/rand` over the alphanumeric alphabet; `secrets.choice` is the equivalent CSPRNG source in Python."""

from __future__ import annotations

import secrets

CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def generate_random_string(length: int) -> str:
    if length < 1:
        return ""
    return "".join(secrets.choice(CHARACTERS) for _ in range(length))


__all__ = ["CHARACTERS", "generate_random_string"]
