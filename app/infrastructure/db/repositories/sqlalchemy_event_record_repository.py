from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.entities import EventRecord, normalize_event_payload
from app.infrastructure.db.models.event_record import EventRecordModel


class SqlAlchemyEventRecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, event_record_id: str) -> EventRecord | None:
        model = self.session.get(EventRecordModel, event_record_id)
        return self._to_domain(model) if model is not None else None

    def add(self, event_record: EventRecord) -> EventRecord:
        model = EventRecordModel(
            id=event_record.id,
            workflow_id=event_record.workflow_id,
            event_type=event_record.event_type,
            payload=event_record.payload,
            received_at=event_record.received_at,
            received_by_user_id=event_record.received_by_user_id,
        )
        self.session.add(model)
        self.session.flush()
        return self._to_domain(model)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    @staticmethod
    def _to_domain(model: EventRecordModel) -> EventRecord:
        return EventRecord(
            id=model.id,
            workflow_id=model.workflow_id,
            event_type=model.event_type,
            payload=normalize_event_payload(model.payload),
            received_at=model.received_at,
            received_by_user_id=model.received_by_user_id,
        )
