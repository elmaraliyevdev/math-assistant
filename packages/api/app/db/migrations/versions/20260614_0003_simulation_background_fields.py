"""Add simulation background execution fields.

Revision ID: 20260614_0003
Revises: 20260614_0002
Create Date: 2026-06-14 18:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260614_0003"
down_revision: str | Sequence[str] | None = "20260614_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "cancel_requested",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "simulations",
        sa.Column("worker_id", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("simulations", "worker_id")
    op.drop_column("simulations", "cancel_requested")
    op.drop_column("simulations", "started_at")
