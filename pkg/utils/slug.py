"""Slug generation. `GenerateSlug` = `slug.Make(name)` + "-" + 4 random lowercase-alphanumeric characters."""

from __future__ import annotations

import re
import secrets
import unicodedata

_SLUG_CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"


def make_slug(text: str) -> str:
    """Approximate gosimple/slug's `Make` for ASCII input."""
    normalized = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    normalized = normalized.lower()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def generate_slug(name: str) -> str:
    suffix = "".join(secrets.choice(_SLUG_CHARSET) for _ in range(4))
    return f"{make_slug(name)}-{suffix}"


__all__ = ["generate_slug", "make_slug"]
