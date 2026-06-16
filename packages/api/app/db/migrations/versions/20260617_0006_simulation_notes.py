"""Simulation notes for mathematics workbench.

Revision ID: 20260617_0006
Revises: 20260616_0005
Create Date: 2026-06-17 10:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260617_0006"
down_revision: str | Sequence[str] | None = "20260616_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "simulation_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_simulation_notes_simulation_id", "simulation_notes", ["simulation_id"])
    op.create_index("ix_simulation_notes_author_id", "simulation_notes", ["author_id"])


def downgrade() -> None:
    op.drop_index("ix_simulation_notes_author_id", table_name="simulation_notes")
    op.drop_index("ix_simulation_notes_simulation_id", table_name="simulation_notes")
    op.drop_table("simulation_notes")
