"""Game version repository tests."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.organization import Organization
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.organization_repository import OrganizationRepository


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

    by_hash = await game_version_repo.get_by_organization_and_content_hash(
        sample_game.organization_id,
        "a" * 64,
    )
    assert by_hash is not None
    assert by_hash.engine_version == "runtime-core@1.8.0"

    by_game = await game_version_repo.list_by_game_id(sample_game.id)
    assert len(by_game) == 1
    assert by_game[0].canonical_json["schemaVersion"] == "1.0.0"


@pytest.mark.asyncio
async def test_game_version_content_hash_unique_within_organization(
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
        organization_id=sample_game.organization_id,
        version=2,
        content_hash="a" * 64,
        canonical_json=sample_canonical_json,
        engine_version="runtime-core@1.8.0",
    )
    with pytest.raises(IntegrityError):
        await game_version_repo.add(duplicate)


@pytest.mark.asyncio
async def test_game_version_same_content_hash_allowed_across_organizations(
    organization_repo: OrganizationRepository,
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    sample_organization: Organization,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_canonical_json: dict[str, str],
) -> None:
    other_org = Organization(name="Other Organization", slug="other-organization")
    other_game = Game(
        organization=other_org,
        name="Other Game",
        description=None,
    )
    await organization_repo.add(sample_organization)
    await organization_repo.add(other_org)
    await game_repo.add(sample_game)
    await game_repo.add(other_game)
    await game_version_repo.add(sample_game_version)

    second_org_version = GameVersion(
        game_id=other_game.id,
        organization_id=other_org.id,
        version=1,
        content_hash="a" * 64,
        canonical_json=sample_canonical_json,
        engine_version="runtime-core@1.8.0",
    )
    created = await game_version_repo.add(second_org_version)
    assert created.id is not None


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
