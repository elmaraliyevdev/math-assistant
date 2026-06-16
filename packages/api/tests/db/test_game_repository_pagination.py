"""Game repository pagination tests."""

from __future__ import annotations

import pytest

from app.db.models.game import Game
from app.db.repositories.game_repository import GameRepository


@pytest.mark.asyncio
async def test_search_paginated_and_count(
    game_repo: GameRepository,
    organization_repo,
    sample_organization,
) -> None:
    await organization_repo.add(sample_organization)
    org_id = sample_organization.id
    await game_repo.add(
        Game(organization_id=org_id, name="Alpha One", description="first"),
    )
    await game_repo.add(
        Game(organization_id=org_id, name="Alpha Two", description="second"),
    )
    await game_repo.add(
        Game(organization_id=org_id, name="Beta", description="third"),
    )

    assert await game_repo.count_search(None, organization_ids=[org_id]) == 3
    assert await game_repo.count_search("Alpha", organization_ids=[org_id]) == 2

    page = await game_repo.search_paginated(
        page=1,
        page_size=2,
        search=None,
        organization_ids=[org_id],
    )
    assert len(page) == 2

    page_two = await game_repo.search_paginated(
        page=2,
        page_size=2,
        search=None,
        organization_ids=[org_id],
    )
    assert len(page_two) == 1
