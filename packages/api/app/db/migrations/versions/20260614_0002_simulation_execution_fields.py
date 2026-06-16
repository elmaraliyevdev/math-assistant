"""Add simulation execution fields.

Revision ID: 20260614_0002
Revises: 20260614_0001
Create Date: 2026-06-14 16:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260614_0002"
down_revision: str | Sequence[str] | None = "20260614_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "simulations",
        sa.Column(
            "bet_minor_units",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "simulations",
        sa.Column(
            "event_log_mode",
            sa.String(length=32),
            nullable=False,
            server_default="none",
        ),
    )
    op.add_column(
        "simulations",
        sa.Column("master_seed", sa.String(length=255), nullable=True),
    )
    op.add_column("simulations", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column(
        "simulation_results",
        sa.Column(
            "mathematics_report",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("simulation_results", "mathematics_report")
    op.drop_column("simulations", "error_message")
    op.drop_column("simulations", "master_seed")
    op.drop_column("simulations", "event_log_mode")
    op.drop_column("simulations", "bet_minor_units")
