"""SimulationResult ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, JsonDocument, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.simulation import Simulation


class SimulationResult(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_results"
    __table_args__ = (
        UniqueConstraint("simulation_id", name="uq_simulation_results_simulation_id"),
    )

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    total_bet_minor_units: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_win_minor_units: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uncapped_win_minor_units: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rtp: Mapped[float] = mapped_column(Float, nullable=False)
    volatility: Mapped[float] = mapped_column(Float, nullable=False)
    hit_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    mathematics_report: Mapped[dict[str, Any]] = mapped_column(
        JsonDocument,
        nullable=False,
    )

    simulation: Mapped[Simulation] = relationship(back_populates="result")
