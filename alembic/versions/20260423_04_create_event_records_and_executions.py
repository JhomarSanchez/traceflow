"""create event records and executions tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260423_04"
down_revision = "20260423_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_by_user_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["received_by_user_id"],
            ["users.id"],
            name=op.f("fk_event_records_received_by_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            name=op.f("fk_event_records_workflow_id_workflows"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event_records")),
    )
    op.create_index(
        op.f("ix_event_records_event_type"),
        "event_records",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_event_records_received_by_user_id"),
        "event_records",
        ["received_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_event_records_workflow_id"),
        "event_records",
        ["workflow_id"],
        unique=False,
    )

    op.create_table(
        "executions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("event_record_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["event_record_id"],
            ["event_records.id"],
            name=op.f("fk_executions_event_record_id_event_records"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            name=op.f("fk_executions_workflow_id_workflows"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_executions")),
        sa.UniqueConstraint("event_record_id", name="uq_executions_event_record_id"),
    )
    op.create_index(op.f("ix_executions_event_record_id"), "executions", ["event_record_id"], unique=False)
    op.create_index(op.f("ix_executions_status"), "executions", ["status"], unique=False)
    op.create_index(op.f("ix_executions_workflow_id"), "executions", ["workflow_id"], unique=False)

    op.create_table(
        "execution_steps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("execution_id", sa.String(length=36), nullable=False),
        sa.Column("workflow_step_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.Column("output_data", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["executions.id"],
            name=op.f("fk_execution_steps_execution_id_executions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_step_id"],
            ["workflow_steps.id"],
            name=op.f("fk_execution_steps_workflow_step_id_workflow_steps"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_execution_steps")),
    )
    op.create_index(
        op.f("ix_execution_steps_execution_id"),
        "execution_steps",
        ["execution_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_execution_steps_workflow_step_id"),
        "execution_steps",
        ["workflow_step_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_execution_steps_workflow_step_id"), table_name="execution_steps")
    op.drop_index(op.f("ix_execution_steps_execution_id"), table_name="execution_steps")
    op.drop_table("execution_steps")
    op.drop_index(op.f("ix_executions_workflow_id"), table_name="executions")
    op.drop_index(op.f("ix_executions_status"), table_name="executions")
    op.drop_index(op.f("ix_executions_event_record_id"), table_name="executions")
    op.drop_table("executions")
    op.drop_index(op.f("ix_event_records_workflow_id"), table_name="event_records")
    op.drop_index(op.f("ix_event_records_received_by_user_id"), table_name="event_records")
    op.drop_index(op.f("ix_event_records_event_type"), table_name="event_records")
    op.drop_table("event_records")
