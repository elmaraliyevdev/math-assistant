"""Simulation repository tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository


@pytest.mark.asyncio
async def test_simulation_crud(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    created = await simulation_repo.add(sample_simulation)

    assert created.status == SimulationStatus.PENDING
    assert created.spin_count == 1000

    fetched = await simulation_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.completed_spin_count == 0


@pytest.mark.asyncio
async def test_simulation_list_by_game_version_id(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await simulation_repo.add(sample_simulation)

    second = Simulation(
        game_version_id=sample_game_version.id,
        spin_count=500,
        status=SimulationStatus.RUNNING,
    )
    await simulation_repo.add(second)

    results = await simulation_repo.list_by_game_version_id(sample_game_version.id)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_simulation_list_by_status(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.COMPLETED
    sample_simulation.completed_at = datetime.now(tz=UTC)
    await simulation_repo.add(sample_simulation)

    completed = await simulation_repo.list_by_status(SimulationStatus.COMPLETED)
    assert len(completed) == 1

    pending = await simulation_repo.list_by_status(SimulationStatus.PENDING)
    assert pending == []


@pytest.mark.asyncio
async def test_simulation_relationship_to_game_version(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    db_session,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await simulation_repo.add(sample_simulation)
    await db_session.commit()

    fetched = await simulation_repo.get_by_id(sample_simulation.id)
    assert fetched is not None
    assert fetched.game_version.content_hash == "a" * 64


@pytest.mark.asyncio
async def test_simulation_get_by_id_missing(
    simulation_repo: SimulationRepository,
) -> None:
    assert await simulation_repo.get_by_id(uuid.uuid4()) is None
