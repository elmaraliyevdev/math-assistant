"""Shard lifecycle and persistence."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_shard_repository import SimulationShardRepository
from app.distributed.accumulator_codec import partial_accumulator_to_dict
from runtime_core.simulation import PartialAccumulator


@dataclass(frozen=True, slots=True)
class ShardService:
    session_factory: async_sessionmaker[AsyncSession]

    async def list_shards(self, simulation_id: uuid.UUID) -> list[SimulationShard]:
        async with self.session_factory() as session:
            return await SimulationShardRepository(session).list_by_simulation_id(
                simulation_id,
            )

    async def mark_running(
        self,
        simulation_id: uuid.UUID,
        shard_index: int,
        *,
        worker_id: str,
        celery_task_id: str | None = None,
    ) -> None:
        async with self.session_factory() as session:
            shards = SimulationShardRepository(session)
            simulations = SimulationRepository(session)
            shard = await shards.get_by_simulation_and_index(simulation_id, shard_index)
            if shard is None:
                return
            shard.status = SimulationShardStatus.RUNNING
            shard.worker_id = worker_id
            shard.celery_task_id = celery_task_id
            shard.started_at = datetime.now(tz=UTC)
            simulation = await simulations.get_by_id(simulation_id)
            if simulation is not None and simulation.status == SimulationStatus.PENDING:
                simulation.status = SimulationStatus.RUNNING
                simulation.started_at = datetime.now(tz=UTC)
                simulation.worker_id = worker_id
            await session.commit()

    async def mark_completed(
        self,
        simulation_id: uuid.UUID,
        shard_index: int,
        *,
        partial: PartialAccumulator,
    ) -> Simulation | None:
        async with self.session_factory() as session:
            shards = SimulationShardRepository(session)
            simulations = SimulationRepository(session)
            shard = await shards.get_by_simulation_and_index(simulation_id, shard_index)
            if shard is None:
                return None
            shard.status = SimulationShardStatus.COMPLETED
            shard.completed_at = datetime.now(tz=UTC)
            shard.partial_result = partial_accumulator_to_dict(partial)
            shard.error_message = None

            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None:
                await session.commit()
                return None

            simulation.completed_shards += 1
            simulation.completed_spin_count += shard.spin_count
            self._refresh_progress(simulation)
            await session.commit()
            await session.refresh(simulation)
            return simulation

    async def mark_failed(
        self,
        simulation_id: uuid.UUID,
        shard_index: int,
        *,
        error_message: str,
    ) -> Simulation | None:
        async with self.session_factory() as session:
            shards = SimulationShardRepository(session)
            simulations = SimulationRepository(session)
            shard = await shards.get_by_simulation_and_index(simulation_id, shard_index)
            if shard is None:
                return None
            shard.status = SimulationShardStatus.FAILED
            shard.completed_at = datetime.now(tz=UTC)
            shard.error_message = error_message

            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None:
                await session.commit()
                return None

            simulation.failed_shards += 1
            self._refresh_progress(simulation)
            await session.commit()
            await session.refresh(simulation)
            return simulation

    async def mark_cancelled_shards(self, simulation_id: uuid.UUID) -> list[str]:
        task_ids: list[str] = []
        async with self.session_factory() as session:
            shards = SimulationShardRepository(session)
            for shard in await shards.list_by_simulation_id(simulation_id):
                if shard.status in {
                    SimulationShardStatus.PENDING,
                    SimulationShardStatus.RUNNING,
                }:
                    shard.status = SimulationShardStatus.CANCELLED
                    shard.completed_at = datetime.now(tz=UTC)
                    if shard.celery_task_id:
                        task_ids.append(shard.celery_task_id)
            await session.commit()
        return task_ids

    async def reset_failed_shards(self, simulation_id: uuid.UUID) -> list[SimulationShard]:
        async with self.session_factory() as session:
            shards = SimulationShardRepository(session)
            simulations = SimulationRepository(session)
            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None:
                return []

            reset: list[SimulationShard] = []
            for shard in await shards.list_failed(simulation_id):
                shard.status = SimulationShardStatus.PENDING
                shard.worker_id = None
                shard.celery_task_id = None
                shard.started_at = None
                shard.completed_at = None
                shard.partial_result = None
                shard.error_message = None
                reset.append(shard)

            if reset:
                simulation.failed_shards = 0
                self._refresh_progress(simulation)
            await session.commit()
            return reset

    @staticmethod
    def _refresh_progress(simulation: Simulation) -> None:
        if simulation.total_shards <= 0:
            simulation.progress_percentage = 0.0
            return
        finished = simulation.completed_shards + simulation.failed_shards
        simulation.progress_percentage = round(
            (finished / simulation.total_shards) * 100,
            2,
        )
