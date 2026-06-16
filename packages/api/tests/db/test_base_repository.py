"""Repository save helper tests."""

from __future__ import annotations

import pytest

from app.db.models.game import Game


@pytest.mark.asyncio
async def test_save_updates_existing_entity(
    game_repo,
    organization_repo,
    sample_organization,
) -> None:
    await organization_repo.add(sample_organization)
    game = await game_repo.add(
        Game(
            organization_id=sample_organization.id,
            name="Before",
            description="old",
        ),
    )
    game.name = "After"
    saved = await game_repo.save(game)
    assert saved.name == "After"
