from __future__ import annotations

from app.domain.entities import EventRecord
from app.domain.exceptions import InvalidEventPayloadError


def test_event_record_create_normalizes_event_type_and_copies_payload() -> None:
    payload = {"email": "user@example.com"}

    event_record = EventRecord.create(
        workflow_id="workflow-1",
        event_type="  user_registered  ",
        payload=payload,
        received_by_user_id="user-1",
    )

    assert event_record.workflow_id == "workflow-1"
    assert event_record.event_type == "user_registered"
    assert event_record.payload == {"email": "user@example.com"}
    assert event_record.payload is not payload


def test_event_record_create_rejects_non_object_payload() -> None:
    try:
        EventRecord.create(
            workflow_id="workflow-1",
            event_type="user_registered",
            payload=None,  # type: ignore[arg-type]
            received_by_user_id="user-1",
        )
    except InvalidEventPayloadError as exc:
        assert exc.code == "invalid_event_payload"
    else:
        raise AssertionError("Invalid event payload error was expected")
