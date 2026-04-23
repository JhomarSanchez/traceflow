from __future__ import annotations

from typing import Protocol

from app.domain.entities import EventRecord


class EventRecordRepository(Protocol):
    def get_by_id(self, event_record_id: str) -> EventRecord | None: ...

    def add(self, event_record: EventRecord) -> EventRecord: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
