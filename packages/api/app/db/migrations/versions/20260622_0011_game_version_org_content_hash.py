"""Scope game version content hash uniqueness to organization."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260622_0011"
down_revision: str | None = "20260621_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "game_versions",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )
    op.execute(
        """
        UPDATE game_versions
        SET organization_id = (
            SELECT organization_id FROM games WHERE games.id = game_versions.game_id
        )
        """,
    )
    op.alter_column("game_versions", "organization_id", nullable=False)
    op.create_foreign_key(
        "fk_game_versions_organization_id",
        "game_versions",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_game_versions_organization_id",
        "game_versions",
        ["organization_id"],
        unique=False,
    )
    op.drop_constraint(
        "uq_game_versions_content_hash",
        "game_versions",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_game_versions_org_content_hash",
        "game_versions",
        ["organization_id", "content_hash"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_game_versions_org_content_hash",
        "game_versions",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_game_versions_content_hash",
        "game_versions",
        ["content_hash"],
    )
    op.drop_index("ix_game_versions_organization_id", table_name="game_versions")
    op.drop_constraint(
        "fk_game_versions_organization_id",
        "game_versions",
        type_="foreignkey",
    )
    op.drop_column("game_versions", "organization_id")
