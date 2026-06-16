"""Simulation activity log service."""

from __future__ import annotations

import uuid
from typing import Any

from app.db.models.simulation_activity_log import SimulationActivityLog
from app.db.repositories.simulation_activity_log_repository import (
    SimulationActivityLogRepository,
)


class ActivityService:
    def __init__(self, repository: SimulationActivityLogRepository) -> None:
        self._repository = repository

    async def record(
        self,
        *,
        simulation_id: uuid.UUID,
        actor_id: uuid.UUID,
        action: str,
        metadata: dict[str, Any] | None = None,
    ) -> SimulationActivityLog:
        entry = SimulationActivityLog(
            simulation_id=simulation_id,
            actor_id=actor_id,
            action=action,
            metadata_json=metadata,
        )
        await self._repository.add(entry)
        return entry

    async def list_for_simulation(
        self,
        simulation_id: uuid.UUID,
    ) -> list[SimulationActivityLog]:
        return await self._repository.list_by_simulation_id(simulation_id)
