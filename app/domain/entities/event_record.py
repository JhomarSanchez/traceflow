from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.entities.workflow import normalize_event_type
from app.domain.exceptions import InvalidEventPayloadError


def normalize_event_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise InvalidEventPayloadError("Event payload must be an object")
    return dict(payload)


@dataclass(slots=True)
class EventRecord:
    id: str
    workflow_id: str
    event_type: str
    payload: dict[str, Any]
    received_at: datetime
    received_by_user_id: str

    @classmethod
    def create(
        cls,
        *,
        workflow_id: str,
        event_type: str,
        payload: Mapping[str, Any],
        received_by_user_id: str,
    ) -> "EventRecord":
        return cls(
            id=str(uuid4()),
            workflow_id=workflow_id,
            event_type=normalize_event_type(event_type),
            payload=normalize_event_payload(payload),
            received_at=datetime.now(UTC),
            received_by_user_id=received_by_user_id,
        )
