"""Persist immutable validation findings on game versions."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260620_0009"
down_revision: str | None = "20260619_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "game_versions",
        sa.Column(
            "validation_passed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "game_versions",
        sa.Column(
            "validation_findings",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )
    op.alter_column("game_versions", "validation_passed", server_default=None)
    op.alter_column("game_versions", "validation_findings", server_default=None)


def downgrade() -> None:
    op.drop_column("game_versions", "validation_findings")
    op.drop_column("game_versions", "validation_passed")
