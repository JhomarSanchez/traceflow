from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.exceptions import InvalidWorkflowDataError


def normalize_workflow_name(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise InvalidWorkflowDataError("Workflow name must not be empty")
    return normalized


def normalize_event_type(event_type: str) -> str:
    normalized = event_type.strip()
    if not normalized:
        raise InvalidWorkflowDataError("Workflow event_type must not be empty")
    return normalized


def normalize_description(description: str | None) -> str | None:
    if description is None:
        return None
    normalized = description.strip()
    return normalized or None


@dataclass(slots=True)
class Workflow:
    id: str
    owner_id: str
    name: str
    description: str | None
    event_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        owner_id: str,
        name: str,
        description: str | None,
        event_type: str,
    ) -> "Workflow":
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            owner_id=owner_id,
            name=normalize_workflow_name(name),
            description=normalize_description(description),
            event_type=normalize_event_type(event_type),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def rename(self, name: str) -> None:
        self.name = normalize_workflow_name(name)
        self.updated_at = datetime.now(UTC)

    def change_description(self, description: str | None) -> None:
        self.description = normalize_description(description)
        self.updated_at = datetime.now(UTC)

    def change_event_type(self, event_type: str) -> None:
        self.event_type = normalize_event_type(event_type)
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def belongs_to(self, owner_id: str) -> bool:
        return self.owner_id == owner_id
