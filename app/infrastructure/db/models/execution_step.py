from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ExecutionStepModel(Base):
    __tablename__ = "execution_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_step_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
