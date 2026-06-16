"""Game ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.game_version import GameVersion
    from app.db.models.organization import Organization


class Game(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "games"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    organization: Mapped[Organization] = relationship(back_populates="games")
    versions: Mapped[list[GameVersion]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )
