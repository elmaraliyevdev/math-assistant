"""Initial persistence schema.

Revision ID: 20260614_0001
Revises:
Create Date: 2026-06-14 14:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260614_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

simulation_status = postgresql.ENUM(
    "pending",
    "running",
    "completed",
    "failed",
    name="simulation_status",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "games",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "canonical_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("engine_version", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_hash", name="uq_game_versions_content_hash"),
    )
    op.create_index(
        op.f("ix_game_versions_game_id"),
        "game_versions",
        ["game_id"],
        unique=False,
    )
    simulation_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "simulations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("game_version_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            simulation_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("spin_count", sa.BigInteger(), nullable=False),
        sa.Column(
            "completed_spin_count",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["game_version_id"],
            ["game_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_simulations_game_version_id",
        "simulations",
        ["game_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_simulations_status",
        "simulations",
        ["status"],
        unique=False,
    )
    op.create_table(
        "simulation_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("simulation_id", sa.Uuid(), nullable=False),
        sa.Column("total_bet_minor_units", sa.BigInteger(), nullable=False),
        sa.Column("total_win_minor_units", sa.BigInteger(), nullable=False),
        sa.Column("uncapped_win_minor_units", sa.BigInteger(), nullable=False),
        sa.Column("rtp", sa.Float(), nullable=False),
        sa.Column("volatility", sa.Float(), nullable=False),
        sa.Column("hit_frequency", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "simulation_id",
            name="uq_simulation_results_simulation_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("simulation_results")
    op.drop_index("ix_simulations_status", table_name="simulations")
    op.drop_index("ix_simulations_game_version_id", table_name="simulations")
    op.drop_table("simulations")
    op.drop_index(op.f("ix_game_versions_game_id"), table_name="game_versions")
    op.drop_table("game_versions")
    op.drop_table("games")
    simulation_status.drop(op.get_bind(), checkfirst=True)
