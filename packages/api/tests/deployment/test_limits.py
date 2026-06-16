"""Deployment limit and safeguard tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import Settings
from app.deployment.limits import (
    MVP_MAX_ACTIVE_SIMULATIONS,
    MVP_MAX_SIMULATION_SPINS,
    resolve_deployment_limits,
    validate_simulation_create,
)
from app.exceptions.domain import (
    ActiveSimulationLimitExceededError,
    SimulationSpinCountExceededError,
)


def test_mvp_defaults() -> None:
    limits = resolve_deployment_limits(Settings(deployment_mode="mvp"))
    assert limits.max_simulation_spin_count == MVP_MAX_SIMULATION_SPINS
    assert limits.max_active_simulations == MVP_MAX_ACTIVE_SIMULATIONS


def test_enterprise_defaults_unlimited_active() -> None:
    limits = resolve_deployment_limits(
        Settings(deployment_mode="enterprise", max_recommended_spin_count=100_000_000),
    )
    assert limits.max_simulation_spin_count == 100_000_000
    assert limits.max_active_simulations is None


def test_explicit_overrides() -> None:
    limits = resolve_deployment_limits(
        Settings(
            deployment_mode="mvp",
            max_simulation_spin_count=5_000_000,
            max_active_simulations=5,
        ),
    )
    assert limits.max_simulation_spin_count == 5_000_000
    assert limits.max_active_simulations == 5


def test_zero_active_means_unlimited() -> None:
    limits = resolve_deployment_limits(
        Settings(deployment_mode="mvp", max_active_simulations=0),
    )
    assert limits.max_active_simulations is None


def test_spin_count_exceeded() -> None:
    limits = resolve_deployment_limits(Settings(deployment_mode="mvp"))
    with pytest.raises(SimulationSpinCountExceededError) as exc:
        validate_simulation_create(
            spin_count=20_000_000,
            active_simulation_count=0,
            limits=limits,
        )
    assert exc.value.details["maxSpinCount"] == MVP_MAX_SIMULATION_SPINS


def test_active_simulation_limit_exceeded() -> None:
    limits = resolve_deployment_limits(Settings(deployment_mode="mvp"))
    with pytest.raises(ActiveSimulationLimitExceededError) as exc:
        validate_simulation_create(
            spin_count=1000,
            active_simulation_count=2,
            limits=limits,
        )
    assert exc.value.status_code == 429
    assert exc.value.details["maxActiveSimulations"] == 2


@pytest.mark.asyncio
async def test_create_simulation_rejects_excessive_spins() -> None:
    from app.auth.context import AuthContext
    from app.db.models.organization_member import OrganizationRole
    from app.schemas.simulations import CreateSimulationRequest
    from app.services.simulation_service import SimulationService

    game_version_id = uuid.uuid4()
    game_id = uuid.uuid4()
    org_id = uuid.uuid4()

    game_version = MagicMock()
    game_version.game_id = game_id
    game = MagicMock()
    game.organization_id = org_id

    auth = MagicMock(spec=AuthContext)
    auth.organization_ids = [org_id]
    auth.user.id = uuid.uuid4()
    auth.require_role = MagicMock()

    simulations = AsyncMock()
    simulations.count_active = AsyncMock(return_value=0)
    game_versions = AsyncMock()
    game_versions.get_by_id_for_organizations = AsyncMock(return_value=game_version)
    games = AsyncMock()
    games.get_by_id_for_organizations = AsyncMock(return_value=game)

    service = SimulationService(
        simulations=simulations,
        simulation_results=AsyncMock(),
        simulation_notes=AsyncMock(),
        game_versions=game_versions,
        games=games,
        settings=Settings(deployment_mode="mvp"),
    )

    with pytest.raises(SimulationSpinCountExceededError):
        await service.create_simulation(
            auth,
            CreateSimulationRequest(
                game_version_id=game_version_id,
                spin_count=20_000_000,
            ),
        )


@pytest.mark.asyncio
async def test_create_simulation_rejects_when_active_limit_reached() -> None:
    from app.auth.context import AuthContext
    from app.schemas.simulations import CreateSimulationRequest
    from app.services.simulation_service import SimulationService

    game_version_id = uuid.uuid4()
    game_id = uuid.uuid4()
    org_id = uuid.uuid4()

    game_version = MagicMock()
    game_version.game_id = game_id
    game = MagicMock()
    game.organization_id = org_id

    auth = MagicMock(spec=AuthContext)
    auth.organization_ids = [org_id]
    auth.user.id = uuid.uuid4()
    auth.require_role = MagicMock()

    simulations = AsyncMock()
    simulations.count_active = AsyncMock(return_value=2)
    game_versions = AsyncMock()
    game_versions.get_by_id_for_organizations = AsyncMock(return_value=game_version)
    games = AsyncMock()
    games.get_by_id_for_organizations = AsyncMock(return_value=game)

    service = SimulationService(
        simulations=simulations,
        simulation_results=AsyncMock(),
        simulation_notes=AsyncMock(),
        game_versions=game_versions,
        games=games,
        settings=Settings(deployment_mode="mvp"),
    )

    with pytest.raises(ActiveSimulationLimitExceededError):
        await service.create_simulation(
            auth,
            CreateSimulationRequest(
                game_version_id=game_version_id,
                spin_count=1000,
            ),
        )
