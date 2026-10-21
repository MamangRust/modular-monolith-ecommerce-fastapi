"""Email event envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass
class EmailEnvelope:
    event_type: str
    email: str
    subject: str
    body: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    schema_version: int = 1
    occurred_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    metadata: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Consumer contract (`EmailEnvelope.IsValid`): non-empty event_id, schema_version == 1, event_type, email, subject AND body. Invalid events must never reach SMTP."""
        return bool(
            self.event_id
            and self.schema_version == 1
            and self.event_type
            and self.email
            and self.subject
            and self.body
        )

    def to_json(self) -> str:
        import json

        payload: dict = {
            "event_id": self.event_id,
            "schema_version": self.schema_version,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at,
            "email": self.email,
            "subject": self.subject,
            "body": self.body,
        }
        if self.metadata:
            payload["metadata"] = self.metadata
        return json.dumps(payload)

    @staticmethod
    def from_json(raw: str | bytes) -> EmailEnvelope:
        import json

        data = json.loads(raw)
        return EmailEnvelope(
            event_type=data.get("event_type", ""),
            email=data.get("email", ""),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
            event_id=data.get("event_id", ""),
            schema_version=data.get("schema_version", 1),
            occurred_at=data.get("occurred_at", ""),
            metadata=data.get("metadata") or {},
        )


def new_email(event_type: str, email: str, subject: str, body: str) -> EmailEnvelope:
    return EmailEnvelope(event_type=event_type, email=email, subject=subject, body=body)


def marshal_email(event_type: str, email: str, subject: str, body: str) -> str:
    return new_email(event_type, email, subject, body).to_json()
