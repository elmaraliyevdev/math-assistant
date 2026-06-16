"""Direct service layer tests."""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from app.auth.context import AuthContext
from app.db.models.game import Game
from app.dependencies import _session_factory, get_db_session
from app.exceptions.domain import GameNotFoundError, ValidationFailedError
from app.schemas.game_versions import CreateGameVersionRequest
from app.schemas.games import CreateGameRequest, UpdateGameRequest
from app.services.game_service import GameService
from app.services.game_version_service import GameVersionService
from app.services.validation_service import ValidationService


@pytest.mark.asyncio
async def test_game_service_crud(
    db_session: AsyncSession,
    auth_context: AuthContext,
) -> None:
    service = GameService.from_session(db_session)
    org_id = auth_context.organization_ids[0]

    created = await service.create_game(
        auth_context,
        CreateGameRequest(
            name="Service Game",
            description="desc",
            organization_id=org_id,
        ),
    )
    assert created.name == "Service Game"

    fetched = await service.get_game(auth_context, created.id)
    assert fetched.id == created.id

    listed = await service.list_games(
        auth_context,
        page=1,
        page_size=10,
        search="Service",
    )
    assert listed.total == 1

    updated = await service.update_game(
        auth_context,
        created.id,
        UpdateGameRequest(name="Updated Only"),
    )
    assert updated.name == "Updated Only"

    await service.delete_game(auth_context, created.id)
    with pytest.raises(GameNotFoundError):
        await service.get_game(auth_context, created.id)


@pytest.mark.asyncio
async def test_game_version_service_create_and_list(
    db_session: AsyncSession,
    auth_context: AuthContext,
    valid_canonical_json: dict,
) -> None:
    game_service = GameService.from_session(db_session)
    org_id = auth_context.organization_ids[0]
    game = await game_service.create_game(
        auth_context,
        CreateGameRequest(name="Version Host", organization_id=org_id),
    )
    version_service = GameVersionService.from_session(
        db_session,
        ValidationService.create(),
    )

    created = await version_service.create_version(
        auth_context,
        game.id,
        CreateGameVersionRequest(
            canonical_json=valid_canonical_json,
            engine_version="runtime-core@1.8.0",
        ),
    )
    assert created.version == 1

    versions = await version_service.list_versions(auth_context, game.id)
    assert len(versions) == 1

    detail = await version_service.get_version(auth_context, game.id, created.id)
    assert detail.canonical_json["schemaVersion"] == "1.0.0"


@pytest.mark.asyncio
async def test_game_version_service_validation_failed(
    db_session: AsyncSession,
    auth_context: AuthContext,
    invalid_canonical_json: dict,
) -> None:
    game_service = GameService.from_session(db_session)
    org_id = auth_context.organization_ids[0]
    game = await game_service.create_game(
        auth_context,
        CreateGameRequest(name="Invalid Host", organization_id=org_id),
    )
    version_service = GameVersionService.from_session(
        db_session,
        ValidationService.create(),
    )

    with pytest.raises(ValidationFailedError):
        await version_service.create_version(
            auth_context,
            game.id,
            CreateGameVersionRequest(
                canonical_json=invalid_canonical_json,
                engine_version="runtime-core@1.8.0",
            ),
        )


@pytest.mark.asyncio
async def test_game_version_service_game_not_found(
    db_session: AsyncSession,
    auth_context: AuthContext,
    valid_canonical_json: dict,
) -> None:
    version_service = GameVersionService.from_session(
        db_session,
        ValidationService.create(),
    )
    missing_id = uuid.uuid4()
    with pytest.raises(GameNotFoundError):
        await version_service.list_versions(auth_context, missing_id)


@pytest.mark.asyncio
async def test_get_db_session_commits(db_engine) -> None:
    from app.db.models.organization import Organization

    app = FastAPI()
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession)
    app.state.session_factory = session_factory
    request = Request({"type": "http", "app": app})

    async for session in get_db_session(request):
        organization = Organization(name="Committed Org", slug="committed-org")
        session.add(organization)
        await session.flush()
        session.add(
            Game(
                name="Committed",
                description=None,
                organization_id=organization.id,
            ),
        )

    async with session_factory() as session:
        from app.db.repositories.game_repository import GameRepository

        games = await GameRepository(session).list_all()
        assert len(games) == 1


@pytest.mark.asyncio
async def test_get_db_session_rolls_back_on_error(db_engine) -> None:
    from app.db.models.organization import Organization

    app = FastAPI()
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession)
    app.state.session_factory = session_factory
    request = Request({"type": "http", "app": app})

    with pytest.raises(RuntimeError, match="boom"):
        async for session in get_db_session(request):
            organization = Organization(name="Rollback Org", slug="rollback-org")
            session.add(organization)
            await session.flush()
            session.add(
                Game(
                    name="Rollback",
                    description=None,
                    organization_id=organization.id,
                ),
            )
            raise RuntimeError("boom")


def test_session_factory_requires_configuration() -> None:
    request = Request({"type": "http", "app": FastAPI()})
    with pytest.raises(RuntimeError, match="session factory not configured"):
        _session_factory(request)


@pytest.mark.asyncio
async def test_game_version_service_duplicate_hash(
    db_session: AsyncSession,
    auth_context: AuthContext,
    valid_canonical_json: dict,
) -> None:
    from app.exceptions.domain import DuplicateGameVersionError

    game_service = GameService.from_session(db_session)
    org_id = auth_context.organization_ids[0]
    game = await game_service.create_game(
        auth_context,
        CreateGameRequest(name="Dup Host", organization_id=org_id),
    )
    version_service = GameVersionService.from_session(
        db_session,
        ValidationService.create(),
    )
    request = CreateGameVersionRequest(
        canonical_json=valid_canonical_json,
        engine_version="runtime-core@1.8.0",
    )
    await version_service.create_version(auth_context, game.id, request)
    with pytest.raises(DuplicateGameVersionError):
        await version_service.create_version(auth_context, game.id, request)


@pytest.mark.asyncio
async def test_game_version_service_get_version_not_found(
    db_session: AsyncSession,
    auth_context: AuthContext,
) -> None:
    from app.exceptions.domain import GameVersionNotFoundError

    game_service = GameService.from_session(db_session)
    org_id = auth_context.organization_ids[0]
    game = await game_service.create_game(
        auth_context,
        CreateGameRequest(name="Missing Version", organization_id=org_id),
    )
    version_service = GameVersionService.from_session(
        db_session,
        ValidationService.create(),
    )
    with pytest.raises(GameVersionNotFoundError):
        await version_service.get_version(auth_context, game.id, uuid.uuid4())


@pytest.mark.asyncio
async def test_game_version_service_invalid_canonical_json(
    db_session: AsyncSession,
    auth_context: AuthContext,
) -> None:
    game_service = GameService.from_session(db_session)
    org_id = auth_context.organization_ids[0]
    game = await game_service.create_game(
        auth_context,
        CreateGameRequest(name="Bad JSON Host", organization_id=org_id),
    )
    version_service = GameVersionService.from_session(
        db_session,
        ValidationService.create(),
    )
    with pytest.raises(ValidationFailedError) as exc_info:
        await version_service.create_version(
            auth_context,
            game.id,
            CreateGameVersionRequest(
                canonical_json={"schemaVersion": "1.0.0"},
                engine_version="runtime-core@1.8.0",
            ),
        )
    assert exc_info.value.details["findings"][0]["code"] == "CANONICAL_JSON_INVALID"
