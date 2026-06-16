"""Platform event helpers for background jobs."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models.notification import NotificationType
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.observability.metrics import SIMULATIONS_TOTAL
from app.services.notification_service import NotificationService


async def notify_simulation_finished(
    session: AsyncSession,
    simulation: Simulation,
) -> None:
    if simulation.created_by_user_id is None:
        return

    notifications = NotificationService.from_session(session)
    game_versions = GameVersionRepository(session)
    games = GameRepository(session)

    organization_id = None
    game_version = await game_versions.get_by_id(simulation.game_version_id)
    if game_version is not None:
        game = await games.get_by_id(game_version.game_id)
        if game is not None:
            organization_id = game.organization_id

    if simulation.status == SimulationStatus.COMPLETED:
        SIMULATIONS_TOTAL.labels(status="completed").inc()
        await notifications.create_notification(
            user_id=simulation.created_by_user_id,
            notification_type=NotificationType.SIMULATION_COMPLETED,
            title="Simulation completed",
            message=f"Simulation {simulation.id} finished successfully.",
            organization_id=organization_id,
            entity_type="simulation",
            entity_id=simulation.id,
        )
    elif simulation.status == SimulationStatus.FAILED:
        SIMULATIONS_TOTAL.labels(status="failed").inc()
        await notifications.create_notification(
            user_id=simulation.created_by_user_id,
            notification_type=NotificationType.SIMULATION_FAILED,
            title="Simulation failed",
            message=simulation.error_message or f"Simulation {simulation.id} failed.",
            organization_id=organization_id,
            entity_type="simulation",
            entity_id=simulation.id,
        )


async def notify_simulation_finished_by_id(
    session_factory: async_sessionmaker[AsyncSession],
    simulation_id: uuid.UUID,
) -> None:
    async with session_factory() as session:
        simulations = SimulationRepository(session)
        simulation = await simulations.get_by_id(simulation_id)
        if simulation is None:
            return
        await notify_simulation_finished(session, simulation)
        await session.commit()
