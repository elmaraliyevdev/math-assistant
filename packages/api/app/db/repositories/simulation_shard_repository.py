"""Simulation shard repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.simulation_shard import SimulationShard, SimulationShardStatus
from app.db.repositories.base import BaseRepository


class SimulationShardRepository(BaseRepository[SimulationShard]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SimulationShard)

    async def list_by_simulation_id(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationShard]:
        result = await self._session.scalars(
            select(SimulationShard)
            .where(SimulationShard.simulation_id == simulation_id)
            .order_by(SimulationShard.shard_index.asc()),
        )
        return list(result.all())

    async def get_by_simulation_and_index(
        self,
        simulation_id: uuid.UUID,
        shard_index: int,
    ) -> SimulationShard | None:
        result = await self._session.scalars(
            select(SimulationShard).where(
                SimulationShard.simulation_id == simulation_id,
                SimulationShard.shard_index == shard_index,
            ),
        )
        return result.first()

    async def list_by_status(
        self,
        simulation_id: uuid.UUID,
        status: SimulationShardStatus,
    ) -> list[SimulationShard]:
        result = await self._session.scalars(
            select(SimulationShard).where(
                SimulationShard.simulation_id == simulation_id,
                SimulationShard.status == status,
            ),
        )
        return list(result.all())

    async def list_failed(self, simulation_id: uuid.UUID) -> list[SimulationShard]:
        return await self.list_by_status(simulation_id, SimulationShardStatus.FAILED)

    async def list_pending(self, simulation_id: uuid.UUID) -> list[SimulationShard]:
        return await self.list_by_status(simulation_id, SimulationShardStatus.PENDING)
