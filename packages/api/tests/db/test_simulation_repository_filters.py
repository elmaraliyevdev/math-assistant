"""Simulation repository filter tests."""

from __future__ import annotations

import pytest

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository


@pytest.mark.asyncio
async def test_search_paginated_with_filters(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    sample_game: Game,
    sample_canonical_json: dict,
) -> None:
    await game_repo.add(sample_game)
    version = await game_version_repo.add(
        GameVersion(
            game_id=sample_game.id,
            version=1,
            content_hash="d" * 64,
            canonical_json=sample_canonical_json,
            engine_version="runtime-core@1.8.0",
        ),
    )
    await simulation_repo.add(
        Simulation(
            game_version_id=version.id,
            status=SimulationStatus.COMPLETED,
            spin_count=100,
            completed_spin_count=100,
            bet_minor_units=100,
            event_log_mode="none",
        ),
    )
    await simulation_repo.add(
        Simulation(
            game_version_id=version.id,
            status=SimulationStatus.FAILED,
            spin_count=50,
            bet_minor_units=100,
            event_log_mode="none",
            error_message="failed",
        ),
    )

    completed = await simulation_repo.search_paginated(
        page=1,
        page_size=10,
        status=SimulationStatus.COMPLETED,
        game_version_id=version.id,
    )
    assert len(completed) == 1
    assert await simulation_repo.count_filtered(
        status=SimulationStatus.COMPLETED,
        game_version_id=version.id,
    ) == 1
