"""SimulationResult repository tests."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.simulation import Simulation
from app.db.models.simulation_result import SimulationResult
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_result_repository import SimulationResultRepository


@pytest.mark.asyncio
async def test_simulation_result_crud(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    simulation_result_repo: SimulationResultRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
    sample_simulation_result: SimulationResult,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await simulation_repo.add(sample_simulation)
    created = await simulation_result_repo.add(sample_simulation_result)

    assert created.rtp == 0.96
    assert created.total_bet_minor_units == 100_000

    by_simulation = await simulation_result_repo.get_by_simulation_id(
        sample_simulation.id,
    )
    assert by_simulation is not None
    assert by_simulation.volatility == 3.2


@pytest.mark.asyncio
async def test_simulation_result_simulation_id_unique(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    simulation_result_repo: SimulationResultRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
    sample_simulation_result: SimulationResult,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await simulation_repo.add(sample_simulation)
    await simulation_result_repo.add(sample_simulation_result)

    duplicate = SimulationResult(
        simulation_id=sample_simulation.id,
        total_bet_minor_units=1,
        total_win_minor_units=1,
        uncapped_win_minor_units=1,
        rtp=0.5,
        volatility=1.0,
        hit_frequency=0.1,
        mathematics_report={"rtp": {"rtp": 0.5, "uncappedRtp": 0.5}},
    )
    with pytest.raises(IntegrityError):
        await simulation_result_repo.add(duplicate)


@pytest.mark.asyncio
async def test_simulation_result_relationship(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    simulation_result_repo: SimulationResultRepository,
    db_session,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
    sample_simulation_result: SimulationResult,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await simulation_repo.add(sample_simulation)
    await simulation_result_repo.add(sample_simulation_result)
    await db_session.commit()

    fetched = await simulation_result_repo.get_by_id(sample_simulation_result.id)
    assert fetched is not None
    assert fetched.simulation.spin_count == 1000
    assert fetched.simulation_id == sample_simulation.id


@pytest.mark.asyncio
async def test_simulation_result_get_by_simulation_id_missing(
    simulation_result_repo: SimulationResultRepository,
) -> None:
    assert await simulation_result_repo.get_by_simulation_id(uuid.uuid4()) is None
