"""Distributed simulation tables.

Revision ID: 20260619_0008
Revises: 20260618_0007
Create Date: 2026-06-19 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260619_0008"
down_revision: str | Sequence[str] | None = "20260618_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column("total_shards", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "simulations",
        sa.Column("completed_shards", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "simulations",
        sa.Column("failed_shards", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "progress_percentage",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "distributed_execution",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_table(
        "simulation_shards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("shard_index", sa.Integer(), nullable=False),
        sa.Column("spin_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
                name="simulation_shard_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("worker_id", sa.String(length=128), nullable=True),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("partial_result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_simulation_shards_simulation_id",
        "simulation_shards",
        ["simulation_id"],
    )
    op.create_index(
        "ix_simulation_shards_simulation_shard_index",
        "simulation_shards",
        ["simulation_id", "shard_index"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_simulation_shards_simulation_shard_index",
        table_name="simulation_shards",
    )
    op.drop_index("ix_simulation_shards_simulation_id", table_name="simulation_shards")
    op.drop_table("simulation_shards")
    op.drop_column("simulations", "distributed_execution")
    op.drop_column("simulations", "progress_percentage")
    op.drop_column("simulations", "failed_shards")
    op.drop_column("simulations", "completed_shards")
    op.drop_column("simulations", "total_shards")
