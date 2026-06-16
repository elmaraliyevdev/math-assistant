"""Distributed simulation monitoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models.simulation import Simulation, SimulationStatus
from app.schemas.distributed import (
    SimulationQueueResponse,
    WorkerHealthResponse,
    WorkerListResponse,
    WorkerStatusItem,
)


@dataclass(frozen=True, slots=True)
class MonitoringService:
    session_factory: async_sessionmaker[AsyncSession]

    def list_workers(self) -> WorkerListResponse:
        from app.distributed.celery_app import celery_app

        inspect = celery_app.control.inspect(timeout=1.0)
        active = inspect.active() or {}
        stats = inspect.stats() or {}
        items: list[WorkerStatusItem] = []
        for worker_name, worker_stats in stats.items():
            active_tasks = len(active.get(worker_name, []))
            items.append(
                WorkerStatusItem(
                    worker_id=worker_name,
                    status="online",
                    active_tasks=active_tasks,
                    processed_tasks=int(worker_stats.get("total", {}).get("tasks.simulation", 0)),
                ),
            )
        return WorkerListResponse(
            active_workers=len(items),
            items=items,
        )

    def worker_health(self) -> WorkerHealthResponse:
        workers = self.list_workers()
        return WorkerHealthResponse(
            healthy=workers.active_workers > 0,
            active_workers=workers.active_workers,
            checked_at=datetime.now(tz=UTC),
        )

    async def queue_summary(self) -> SimulationQueueResponse:
        from app.distributed.celery_app import celery_app

        async with self.session_factory() as session:
            pending_tasks = int(
                await session.scalar(
                    select(func.count())
                    .select_from(Simulation)
                    .where(Simulation.status == SimulationStatus.PENDING),
                )
                or 0,
            )
            running_tasks = int(
                await session.scalar(
                    select(func.count())
                    .select_from(Simulation)
                    .where(Simulation.status == SimulationStatus.RUNNING),
                )
                or 0,
            )
            completed_tasks = int(
                await session.scalar(
                    select(func.count())
                    .select_from(Simulation)
                    .where(Simulation.status == SimulationStatus.COMPLETED),
                )
                or 0,
            )
            failed_tasks = int(
                await session.scalar(
                    select(func.count())
                    .select_from(Simulation)
                    .where(Simulation.status == SimulationStatus.FAILED),
                )
                or 0,
            )
            since = datetime.now(tz=UTC) - timedelta(hours=24)
            result = await session.execute(
                select(Simulation.started_at, Simulation.completed_at).where(
                    Simulation.status == SimulationStatus.COMPLETED,
                    Simulation.started_at.is_not(None),
                    Simulation.completed_at.is_not(None),
                    Simulation.completed_at >= since,
                ),
            )
            total_seconds = 0.0
            count = 0
            for started_at, completed_at in result.all():
                if started_at and completed_at:
                    total_seconds += (completed_at - started_at).total_seconds()
                    count += 1
            average_duration = total_seconds / count if count else None

        reserved = 0
        try:
            inspect = celery_app.control.inspect(timeout=0.5)
            reserved_map = inspect.reserved() or {}
            reserved = sum(len(tasks) for tasks in reserved_map.values())
        except Exception:
            reserved = 0

        return SimulationQueueResponse(
            pending_tasks=pending_tasks + reserved,
            running_tasks=running_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            average_simulation_duration_seconds=average_duration,
        )
