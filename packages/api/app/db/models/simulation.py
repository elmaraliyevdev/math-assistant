"""Simulation ORM model."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from app.db.models.simulation_workflow import SimulationWorkflowStatus

if TYPE_CHECKING:
    from app.db.models.game_version import GameVersion
    from app.db.models.simulation_activity_log import SimulationActivityLog
    from app.db.models.simulation_approval import SimulationApproval
    from app.db.models.simulation_comment import SimulationComment
    from app.db.models.simulation_note import SimulationNote
    from app.db.models.simulation_result import SimulationResult
    from app.db.models.simulation_review import SimulationReview
    from app.db.models.simulation_shard import SimulationShard


class SimulationStatus(enum.StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Simulation(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "simulations"
    __table_args__ = (
        Index("ix_simulations_status", "status"),
        Index("ix_simulations_game_version_id", "game_version_id"),
    )

    game_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("game_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[SimulationStatus] = mapped_column(
        Enum(
            SimulationStatus,
            name="simulation_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
        ),
        nullable=False,
        default=SimulationStatus.PENDING,
    )
    spin_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    completed_spin_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancel_requested: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    worker_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bet_minor_units: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    event_log_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="none")
    master_seed: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    workflow_status: Mapped[SimulationWorkflowStatus] = mapped_column(
        Enum(
            SimulationWorkflowStatus,
            name="simulation_workflow_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
        ),
        nullable=False,
        default=SimulationWorkflowStatus.DRAFT,
    )
    total_shards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_shards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_shards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    progress_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    distributed_execution: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    game_version: Mapped[GameVersion] = relationship(back_populates="simulations")
    result: Mapped[SimulationResult | None] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
        uselist=False,
    )
    notes: Mapped[list[SimulationNote]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list[SimulationReview]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list[SimulationComment]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    approvals: Mapped[list[SimulationApproval]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    activity_logs: Mapped[list[SimulationActivityLog]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    shards: Mapped[list[SimulationShard]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
