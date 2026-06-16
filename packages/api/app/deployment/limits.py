"""Deployment-mode simulation limits and validation."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.exceptions.domain import (
    ActiveSimulationLimitExceededError,
    SimulationSpinCountExceededError,
)

MVP_MAX_SIMULATION_SPINS = 10_000_000
MVP_MAX_ACTIVE_SIMULATIONS = 2


@dataclass(frozen=True, slots=True)
class DeploymentLimits:
    deployment_mode: str
    max_simulation_spin_count: int
    max_active_simulations: int | None


def resolve_deployment_limits(settings: Settings) -> DeploymentLimits:
    mode = settings.deployment_mode.lower()
    if settings.max_simulation_spin_count is not None:
        max_spins = settings.max_simulation_spin_count
    elif mode == "enterprise":
        max_spins = settings.max_recommended_spin_count
    else:
        max_spins = MVP_MAX_SIMULATION_SPINS

    if settings.max_active_simulations is not None:
        max_active = (
            None
            if settings.max_active_simulations == 0
            else settings.max_active_simulations
        )
    elif mode == "enterprise":
        max_active = None
    else:
        max_active = MVP_MAX_ACTIVE_SIMULATIONS

    if max_active is not None and max_active < 0:
        max_active = None

    return DeploymentLimits(
        deployment_mode=mode,
        max_simulation_spin_count=max_spins,
        max_active_simulations=max_active,
    )


def validate_simulation_create(
    *,
    spin_count: int,
    active_simulation_count: int,
    limits: DeploymentLimits,
) -> None:
    if spin_count > limits.max_simulation_spin_count:
        raise SimulationSpinCountExceededError(
            spin_count=spin_count,
            max_spin_count=limits.max_simulation_spin_count,
            deployment_mode=limits.deployment_mode,
        )

    if (
        limits.max_active_simulations is not None
        and active_simulation_count >= limits.max_active_simulations
    ):
        raise ActiveSimulationLimitExceededError(
            active_simulation_count=active_simulation_count,
            max_active_simulations=limits.max_active_simulations,
            deployment_mode=limits.deployment_mode,
        )
