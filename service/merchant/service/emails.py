"""Merchant email body rendering. renders merchant email bodies with `email.GenerateEmailHTML` (an HTML template). That shared package is scheduled to be with the email worker stage (T14'); until then renders a plain-text body carrying the same message and call-to-action, consistent with the existing auth outbox port."""

from __future__ import annotations


def email_body(message: str, button: str, link: str) -> str:
    return f"{message}\n\n{button}: {link}"


__all__ = ["email_body"]
