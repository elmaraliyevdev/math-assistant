"""Organization ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.game import Game
    from app.db.models.organization_invitation import OrganizationInvitation
    from app.db.models.organization_member import OrganizationMember


class Organization(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    members: Mapped[list[OrganizationMember]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    games: Mapped[list[Game]] = relationship(back_populates="organization")
    invitations: Mapped[list[OrganizationInvitation]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
