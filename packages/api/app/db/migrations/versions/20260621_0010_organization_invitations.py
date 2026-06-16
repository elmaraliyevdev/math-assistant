"""Organization email invitations."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260621_0010"
down_revision: str | None = "20260620_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "developer",
                "viewer",
                name="organization_role",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("invited_by_user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "accepted",
                "declined",
                "expired",
                "cancelled",
                name="invitation_status",
                native_enum=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["invited_by_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "email",
            name="uq_organization_invitations_org_email",
        ),
    )
    op.create_index(
        "ix_organization_invitations_email",
        "organization_invitations",
        ["email"],
    )
    op.create_index(
        "ix_organization_invitations_status",
        "organization_invitations",
        ["status"],
    )
    op.alter_column("organization_invitations", "status", server_default=None)


def downgrade() -> None:
    op.drop_index(
        "ix_organization_invitations_status",
        table_name="organization_invitations",
    )
    op.drop_index(
        "ix_organization_invitations_email",
        table_name="organization_invitations",
    )
    op.drop_table("organization_invitations")
    op.execute(sa.text("DROP TYPE IF EXISTS invitation_status"))
