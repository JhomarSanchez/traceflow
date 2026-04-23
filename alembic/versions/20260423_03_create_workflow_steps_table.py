"""create workflow steps table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260423_03"
down_revision = "20260423_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_steps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("step_type", sa.String(length=64), nullable=False),
        sa.Column("step_config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            name=op.f("fk_workflow_steps_workflow_id_workflows"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_steps")),
        sa.UniqueConstraint(
            "workflow_id",
            "step_order",
            name="uq_workflow_steps_workflow_id_step_order",
        ),
    )
    op.create_index(
        op.f("ix_workflow_steps_workflow_id"),
        "workflow_steps",
        ["workflow_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_workflow_steps_workflow_id"), table_name="workflow_steps")
    op.drop_table("workflow_steps")
