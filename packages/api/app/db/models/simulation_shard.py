"""Simulation shard ORM model for distributed execution."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, JsonDocument, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.simulation import Simulation


class SimulationShardStatus(enum.StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SimulationShard(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulation_shards"
    __table_args__ = (
        Index("ix_simulation_shards_simulation_id", "simulation_id"),
        Index(
            "ix_simulation_shards_simulation_shard_index",
            "simulation_id",
            "shard_index",
            unique=True,
        ),
    )

    simulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        nullable=False,
    )
    shard_index: Mapped[int] = mapped_column(Integer, nullable=False)
    spin_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SimulationShardStatus] = mapped_column(
        Enum(
            SimulationShardStatus,
            name="simulation_shard_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
        ),
        nullable=False,
        default=SimulationShardStatus.PENDING,
    )
    worker_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    partial_result: Mapped[dict[str, Any] | None] = mapped_column(
        JsonDocument,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    simulation: Mapped[Simulation] = relationship(back_populates="shards")
