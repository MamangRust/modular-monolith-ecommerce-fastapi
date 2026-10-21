"""Identifier masking for logs and traces.

Card numbers are sensitive identifiers, so the card service never puts a raw
card number into a span attribute or log field. Masking is for observability
only — never for authentication or persistence."""

from __future__ import annotations


def mask_identifier(value: str) -> str:
    """Keep only the last four characters of `value`.

Matches the expected helper exactly, including the short-input cases:
 `""` -> `""`, and anything of length <= 4 -> `"****"`."""
    if value == "":
        return ""
    if len(value) <= 4:
        return "****"
    return "*" * (len(value) - 4) + value[-4:]


__all__ = ["mask_identifier"]
