"""create workflows table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260423_02"
down_revision = "20260423_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflows",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name=op.f("fk_workflows_owner_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflows")),
    )
    op.create_index(op.f("ix_workflows_event_type"), "workflows", ["event_type"], unique=False)
    op.create_index(op.f("ix_workflows_owner_id"), "workflows", ["owner_id"], unique=False)
    op.create_index(
        "uq_workflows_owner_id_event_type_active",
        "workflows",
        ["owner_id", "event_type"],
        unique=True,
        sqlite_where=sa.text("is_active = 1"),
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.drop_index("uq_workflows_owner_id_event_type_active", table_name="workflows")
    op.drop_index(op.f("ix_workflows_owner_id"), table_name="workflows")
    op.drop_index(op.f("ix_workflows_event_type"), table_name="workflows")
    op.drop_table("workflows")
