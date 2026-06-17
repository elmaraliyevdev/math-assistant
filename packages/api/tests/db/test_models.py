"""Model metadata and cascade behavior tests."""

from __future__ import annotations

import pytest
from sqlalchemy import UniqueConstraint

from app.db.base import Base, JsonDocument
from app.db.models import Game, GameVersion, Simulation, SimulationResult
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_result_repository import SimulationResultRepository


def test_all_models_registered() -> None:
    table_names = set(Base.metadata.tables)
    assert table_names == {
        "audit_logs",
        "games",
        "game_versions",
        "simulations",
        "simulation_results",
        "simulation_shards",
        "simulation_notes",
        "simulation_comments",
        "simulation_reviews",
        "simulation_approvals",
        "simulation_activity_log",
        "notifications",
        "users",
        "organizations",
        "organization_members",
        "organization_invitations",
        "refresh_tokens",
        "user_preferences",
    }


def test_json_document_has_postgresql_variant() -> None:
    from sqlalchemy.dialects import postgresql, sqlite

    pg_type = postgresql.dialect().type_descriptor(JsonDocument)
    sqlite_type = sqlite.dialect().type_descriptor(JsonDocument)
    assert pg_type.__class__.__name__ == "_PGJSON"
    assert sqlite_type.__class__.__name__ == "_SQliteJson"


def test_game_version_org_content_hash_unique_constraint() -> None:
    table = GameVersion.__table__
    unique_constraints = [
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint) and constraint.name
    ]
    assert "uq_game_versions_org_content_hash" in unique_constraints


def test_simulation_indexes() -> None:
    index_names = {index.name for index in Simulation.__table__.indexes}
    assert "ix_simulations_status" in index_names
    assert "ix_simulations_game_version_id" in index_names


@pytest.mark.asyncio
async def test_cascade_delete_game_removes_versions(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await game_repo.delete(sample_game)
    assert await game_version_repo.get_by_id(sample_game_version.id) is None


@pytest.mark.asyncio
async def test_cascade_delete_simulation_removes_result(
    game_repo: GameRepository,
    game_version_repo: GameVersionRepository,
    simulation_repo: SimulationRepository,
    simulation_result_repo: SimulationResultRepository,
    sample_game: Game,
    sample_game_version: GameVersion,
    sample_simulation: Simulation,
    sample_simulation_result: SimulationResult,
) -> None:
    await game_repo.add(sample_game)
    await game_version_repo.add(sample_game_version)
    await simulation_repo.add(sample_simulation)
    await simulation_result_repo.add(sample_simulation_result)

    await simulation_repo.delete(sample_simulation)
    assert await simulation_result_repo.get_by_id(sample_simulation_result.id) is None
