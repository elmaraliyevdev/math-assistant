"""GameVersion ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, JsonDocument, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.game import Game
    from app.db.models.organization import Organization
    from app.db.models.simulation import Simulation


class GameVersion(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "game_versions"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "content_hash",
            name="uq_game_versions_org_content_hash",
        ),
    )

    game_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_json: Mapped[dict[str, Any]] = mapped_column(JsonDocument, nullable=False)
    engine_version: Mapped[str] = mapped_column(String(64), nullable=False)
    validation_passed: Mapped[bool] = mapped_column(nullable=False, default=True)
    validation_findings: Mapped[list[dict[str, object]]] = mapped_column(
        JsonDocument,
        nullable=False,
        default=list,
    )

    game: Mapped[Game] = relationship(back_populates="versions")
    organization: Mapped[Organization] = relationship()
    simulations: Mapped[list[Simulation]] = relationship(
        back_populates="game_version",
        cascade="all, delete-orphan",
    )
