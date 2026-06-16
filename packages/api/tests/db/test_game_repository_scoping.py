"""Game repository organization scoping tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models.game import Game
from app.db.repositories.game_repository import GameRepository


@pytest.mark.asyncio
async def test_search_with_empty_organization_ids(game_repo: GameRepository) -> None:
    assert await game_repo.count_search(None, organization_ids=[]) == 0
    assert await game_repo.search_paginated(
        page=1,
        page_size=10,
        search=None,
        organization_ids=[],
    ) == []
    assert await game_repo.get_by_id_for_organizations(uuid.uuid4(), []) is None


@pytest.mark.asyncio
async def test_get_by_id_for_organizations(
    game_repo: GameRepository,
    organization_repo,
    sample_organization,
    sample_game,
) -> None:
    await organization_repo.add(sample_organization)
    created = await game_repo.add(sample_game)
    fetched = await game_repo.get_by_id_for_organizations(
        created.id,
        [sample_organization.id],
    )
    assert fetched is not None
    assert fetched.id == created.id

    other_org_id = uuid.uuid4()
    assert await game_repo.get_by_id_for_organizations(created.id, [other_org_id]) is None
