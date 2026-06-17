"""Extended GameVersion repository tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository


@pytest.mark.asyncio
async def test_get_by_id_for_game_and_max_version(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    sample_game: Game,
    sample_canonical_json: dict,
) -> None:
    await game_repo.add(sample_game)
    first = await game_version_repo.add(
        GameVersion(
            game_id=sample_game.id,
            organization_id=sample_game.organization_id,
            version=1,
            content_hash="b" * 64,
            canonical_json=sample_canonical_json,
            engine_version="runtime-core@1.8.0",
        ),
    )
    second = await game_version_repo.add(
        GameVersion(
            game_id=sample_game.id,
            organization_id=sample_game.organization_id,
            version=2,
            content_hash="c" * 64,
            canonical_json=sample_canonical_json,
            engine_version="runtime-core@1.8.0",
        ),
    )

    assert await game_version_repo.get_max_version(sample_game.id) == 2
    assert await game_version_repo.get_by_id_for_game(first.id, sample_game.id) == first
    assert await game_version_repo.get_by_id_for_game(first.id, uuid.uuid4()) is None
    assert await game_version_repo.get_by_id_for_game(uuid.uuid4(), sample_game.id) is None
    assert second.version == 2
