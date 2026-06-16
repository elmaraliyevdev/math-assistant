"""Simulation repository organization scoping tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models.simulation import Simulation, SimulationStatus
from app.db.repositories.simulation_repository import SimulationRepository


@pytest.mark.asyncio
async def test_search_with_empty_organization_ids(
    simulation_repo: SimulationRepository,
) -> None:
    assert await simulation_repo.count_filtered(organization_ids=[]) == 0
    assert await simulation_repo.search_paginated(
        page=1,
        page_size=10,
        organization_ids=[],
    ) == []


@pytest.mark.asyncio
async def test_get_by_id_for_organizations(
    game_repo,
    game_version_repo,
    simulation_repo,
    sample_game,
    sample_game_version,
    sample_simulation,
    sample_organization,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    sample_simulation.status = SimulationStatus.COMPLETED
    created = await simulation_repo.add(sample_simulation)

    fetched = await simulation_repo.get_by_id_for_organizations(
        created.id,
        [sample_organization.id],
    )
    assert fetched is not None
    assert fetched.id == created.id

    assert await simulation_repo.get_by_id_for_organizations(
        created.id,
        [uuid.uuid4()],
    ) is None
