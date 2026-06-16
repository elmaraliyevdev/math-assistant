"""GameVersion repository tests."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository


@pytest.mark.asyncio
async def test_game_version_crud(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
) -> None:
    await game_repo.add(sample_game)
    created = await game_version_repo.add(sample_game_version)

    assert created.id is not None
    assert created.version == 1

    by_hash = await game_version_repo.get_by_content_hash("a" * 64)
    assert by_hash is not None
    assert by_hash.engine_version == "runtime-core@1.8.0"

    by_game = await game_version_repo.list_by_game_id(sample_game.id)
    assert len(by_game) == 1
    assert by_game[0].canonical_json["schemaVersion"] == "1.0.0"


@pytest.mark.asyncio
async def test_game_version_content_hash_unique(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_canonical_json: dict[str, str],
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)

    duplicate = GameVersion(
        game_id=sample_game.id,
        version=2,
        content_hash="a" * 64,
        canonical_json=sample_canonical_json,
        engine_version="runtime-core@1.8.0",
    )
    with pytest.raises(IntegrityError):
        await game_version_repo.add(duplicate)


@pytest.mark.asyncio
async def test_game_version_relationship_to_game(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    db_session,
    sample_game: Game,
    sample_game_version: GameVersion,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await db_session.commit()

    fetched = await game_version_repo.get_by_id(sample_game_version.id)
    assert fetched is not None
    assert fetched.game.name == "Golden Base 5x3"
    assert fetched.game_id == sample_game.id
