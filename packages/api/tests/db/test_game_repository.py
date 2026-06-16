"""Game repository tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models.game import Game
from app.db.repositories.game_repository import GameRepository


@pytest.mark.asyncio
async def test_game_crud(
    game_repo: GameRepository,
    sample_game: Game,
    sample_organization,
) -> None:
    created = await game_repo.add(sample_game)
    assert created.id is not None
    assert created.name == "Golden Base 5x3"

    fetched = await game_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.description == "Test game"

    by_name = await game_repo.get_by_name_in_organization(
        name="Golden Base 5x3",
        organization_id=sample_organization.id,
    )
    assert by_name is not None
    assert by_name.id == created.id

    all_games = await game_repo.list_all()
    assert len(all_games) == 1

    await game_repo.delete(created)
    assert await game_repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_game_get_by_id_missing(game_repo: GameRepository) -> None:
    assert await game_repo.get_by_id(uuid.uuid4()) is None


@pytest.mark.asyncio
async def test_game_get_by_name_missing(
    game_repo: GameRepository,
    sample_organization,
) -> None:
    assert await game_repo.get_by_name_in_organization(
        name="missing",
        organization_id=sample_organization.id,
    ) is None
