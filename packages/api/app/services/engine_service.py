"""Engine metadata service — runtime_core public APIs only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from runtime_core.plugins import BUILT_IN_PLUGINS
from runtime_core.runtime import (
    ENGINE_VERSION,
    RNGAlgorithm,
    SeedDerivationPolicy,
    default_rng_service_config,
)
from runtime_core.validation import VALIDATOR_VERSION
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.deployment.limits import resolve_deployment_limits
from app.db.repositories.simulation_repository import SimulationRepository
from app.schemas.engine import EngineVersionResponse, RngCapabilities, SupportedPlugin
from app.schemas.health import HealthResponse


@dataclass(frozen=True, slots=True)
class EngineService:
    settings: Settings

    def health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            timestamp=datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        )

    async def engine_version(self, session: AsyncSession) -> EngineVersionResponse:
        rng_config = default_rng_service_config()
        limits = resolve_deployment_limits(self.settings)
        active_count = await SimulationRepository(session).count_active()
        max_spins = min(
            self.settings.max_recommended_spin_count,
            limits.max_simulation_spin_count,
        )
        return EngineVersionResponse(
            engine_version=ENGINE_VERSION,
            validator_version=VALIDATOR_VERSION,
            supported_plugins=[
                SupportedPlugin(
                    pluginId=plugin.plugin_id,
                    version=plugin.version,
                )
                for plugin in BUILT_IN_PLUGINS
            ],
            rng=RngCapabilities(
                algorithm=str(rng_config.algorithm or RNGAlgorithm.PCG64),
                policy=str(rng_config.policy or SeedDerivationPolicy.V1_HASH_SHARD),
            ),
            max_recommended_spin_count=max_spins,
            deployment_mode=limits.deployment_mode,
            max_simulation_spin_count=limits.max_simulation_spin_count,
            max_active_simulations=limits.max_active_simulations,
            active_simulation_count=active_count,
        )
