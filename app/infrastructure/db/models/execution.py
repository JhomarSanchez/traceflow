from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ExecutionModel(Base):
    __tablename__ = "executions"
    __table_args__ = (
        UniqueConstraint("event_record_id", name="uq_executions_event_record_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("event_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
