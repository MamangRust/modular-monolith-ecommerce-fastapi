"""Unit tests for the email HTML template and envelope contract."""

from __future__ import annotations

from pkg.email import generate_email_html
from pkg.event import EmailEnvelope


def test_template_substitutes_known_fields() -> None:
    html = generate_email_html(
        {
            "Title": "Transaction Successful",
            "Message": "Your transaction of 12765 has been processed successfully.",
            "Button": "View History",
            "Link": "https://sanedge.example.com/transaction/history",
        }
    )
    assert "<h1>Transaction Successful</h1>" in html
    assert "Your transaction of 12765 has been processed successfully." in html
    assert 'href="https://sanedge.example.com/transaction/history"' in html
    assert ">View History</a>" in html
    assert "contact support@sanedge.com" in html


def test_template_missing_subject_renders_empty_title() -> None:
    # a map lookup of a missing key renders the zero value (empty string).
    html = generate_email_html({"Title": "T", "Message": "M", "Button": "B", "Link": "L"})
    assert "<title></title>" in html


def test_template_missing_keys_render_empty() -> None:
    html = generate_email_html({})
    assert "<h1></h1>" in html and "<p></p>" in html


def _envelope(**overrides: object) -> EmailEnvelope:
    values: dict[str, object] = {
        "event_type": "transaction.created",
        "email": "to@example.com",
        "subject": "s",
        "body": "b",
        "event_id": "evt-1",
        "schema_version": 1,
    }
    values.update(overrides)
    return EmailEnvelope(**values)  # type: ignore[arg-type]


def test_envelope_is_valid_contract() -> None:
    assert _envelope().is_valid() is True
    # Every contract field is required (EmailEnvelope.IsValid).
    assert _envelope(body="").is_valid() is False
    assert _envelope(subject="").is_valid() is False
    assert _envelope(event_id="").is_valid() is False
    assert _envelope(schema_version=2).is_valid() is False
    assert _envelope(email="").is_valid() is False
    assert _envelope(event_type="").is_valid() is False


def test_envelope_json_round_trip() -> None:
    envelope = EmailEnvelope(
        event_type="merchant.created",
        email="a@b.com",
        subject="s",
        body="b",
        event_id="evt-9",
        schema_version=1,
    )
    parsed = EmailEnvelope.from_json(envelope.to_json())
    assert parsed == envelope
