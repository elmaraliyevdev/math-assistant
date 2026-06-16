"""API response schemas for engine metadata."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SupportedPlugin(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    plugin_id: str = Field(alias="pluginId")
    version: str


class RngCapabilities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    algorithm: str
    policy: str


class EngineVersionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    engine_version: str = Field(alias="engineVersion")
    validator_version: str = Field(alias="validatorVersion")
    supported_plugins: list[SupportedPlugin] = Field(alias="supportedPlugins")
    rng: RngCapabilities
    max_recommended_spin_count: int = Field(alias="maxRecommendedSpinCount")
    deployment_mode: str = Field(alias="deploymentMode")
    max_simulation_spin_count: int = Field(alias="maxSimulationSpinCount")
    max_active_simulations: int | None = Field(alias="maxActiveSimulations")
    active_simulation_count: int = Field(alias="activeSimulationCount")
