"""Distributed simulation orchestration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from runtime_core.simulation import assign_shards
from runtime_core.runtime.events import EventLogMode
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.simulation import build_simulation_profile
from app.adapters.simulation_sharding import compute_shard_count
from app.config import Settings
from app.db.models.simulation import Simulation
from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_shard_repository import SimulationShardRepository
from app.jobs.simulation_logging import log_simulation_event


@dataclass(frozen=True, slots=True)
class OrchestrationService:
    session_factory: async_sessionmaker[AsyncSession]
    settings: Settings

    def compute_shard_count_for(self, spin_count: int) -> int:
        return compute_shard_count(
            spin_count,
            min_shards=self.settings.simulation_shard_min,
            max_shards=self.settings.simulation_shard_max,
            spins_per_shard=self.settings.simulation_spins_per_shard,
        )

    async def prepare_shards(self, simulation_id: uuid.UUID) -> list[SimulationShard]:
        async with self.session_factory() as session:
            simulations = SimulationRepository(session)
            shards_repo = SimulationShardRepository(session)
            game_versions = GameVersionRepository(session)

            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None:
                return []

            game_version = await game_versions.get_by_id(simulation.game_version_id)
            if game_version is None:
                return []

            shard_count = self.compute_shard_count_for(simulation.spin_count)
            profile = build_simulation_profile(
                simulation_id=simulation.id,
                spin_count=simulation.spin_count,
                bet_minor_units=simulation.bet_minor_units,
                event_log_mode=EventLogMode(simulation.event_log_mode),
                master_seed=simulation.master_seed,
                engine_version=game_version.engine_version,
                shard_count=shard_count,
            )
            assignments = assign_shards(
                profile.spin_count,
                profile.shard_count,
                master_seed=profile.master_seed,
                simulation_run_id=profile.simulation_run_id,
            )

            created: list[SimulationShard] = []
            for assignment in assignments:
                if assignment.spin_count <= 0:
                    continue
                shard = SimulationShard(
                    simulation_id=simulation.id,
                    shard_index=assignment.shard_index,
                    spin_count=assignment.spin_count,
                    status=SimulationShardStatus.PENDING,
                )
                await shards_repo.add(shard)
                created.append(shard)

            simulation.distributed_execution = True
            simulation.total_shards = len(created)
            simulation.completed_shards = 0
            simulation.failed_shards = 0
            simulation.progress_percentage = 0.0
            await session.commit()
            log_simulation_event(
                "simulation_shards_prepared",
                simulation_id=str(simulation_id),
                total_shards=len(created),
                shard_count=shard_count,
            )
            return created

    async def dispatch_shards(self, simulation_id: uuid.UUID) -> int:
        from app.distributed.tasks import run_simulation_shard

        async with self.session_factory() as session:
            shards = await SimulationShardRepository(session).list_by_simulation_id(
                simulation_id,
            )

        dispatched = 0
        for shard in shards:
            if shard.status != SimulationShardStatus.PENDING:
                continue
            result = run_simulation_shard.delay(
                str(simulation_id),
                shard.shard_index,
            )
            async with self.session_factory() as session:
                row = await SimulationShardRepository(session).get_by_simulation_and_index(
                    simulation_id,
                    shard.shard_index,
                )
                if row is not None:
                    row.celery_task_id = result.id
                    await session.commit()
            dispatched += 1
        return dispatched

    async def orchestrate(self, simulation_id: uuid.UUID) -> None:
        shards = await self.prepare_shards(simulation_id)
        if not shards:
            return
        await self.dispatch_shards(simulation_id)

    async def retry_failed(self, simulation_id: uuid.UUID) -> int:
        from app.distributed.shard_service import ShardService
        from app.distributed.tasks import run_simulation_shard

        shard_service = ShardService(self.session_factory)
        reset = await shard_service.reset_failed_shards(simulation_id)
        dispatched = 0
        for shard in reset:
            result = run_simulation_shard.delay(str(simulation_id), shard.shard_index)
            async with self.session_factory() as session:
                row = await SimulationShardRepository(session).get_by_simulation_and_index(
                    simulation_id,
                    shard.shard_index,
                )
                if row is not None:
                    row.celery_task_id = result.id
                    await session.commit()
            dispatched += 1
        return dispatched
