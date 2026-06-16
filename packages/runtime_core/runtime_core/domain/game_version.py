"""Canonical GameVersion domain model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from runtime_core.domain.plugins import (
    Paytable,
    PluginRef,
    ReelSet,
    RtpCategoryRegistryDoc,
    RuntimeLimits,
    WinModel,
)
from runtime_core.domain.state_machine import StateMachine


class GameVersionMeta(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    project_id: str = Field(alias="projectId")
    version_number: int = Field(alias="versionNumber")
    status: str
    created_at: str = Field(alias="createdAt")
    published_at: str | None = Field(default=None, alias="publishedAt")
    created_by: str | None = Field(default=None, alias="createdBy")
    label: str | None = None
    source: str | None = None


class RtpTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    percent: float
    tolerance: float | None = None


class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    title: str
    description: str | None = None
    tags: list[str] | None = None
    rtp_target: RtpTarget | None = Field(default=None, alias="rtpTarget")
    volatility_target: str | None = Field(default=None, alias="volatilityTarget")


class GridSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    reels: int
    rows: int
    index_origin: str | None = Field(default=None, alias="indexOrigin")


class GameConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    grid: GridSpec
    default_reel_set_id: str = Field(alias="defaultReelSetId")


class BetModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: str
    line_count: int | None = Field(default=None, alias="lineCount")
    coin_value_scale: int = Field(alias="coinValueScale")
    default_coin_value: int = Field(alias="defaultCoinValue")
    min_coin_value: int | None = Field(default=None, alias="minCoinValue")
    max_coin_value: int | None = Field(default=None, alias="maxCoinValue")
    total_bet_minor_units: int | None = Field(default=None, alias="totalBetMinorUnits")


class SessionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    root_machine_id: str = Field(alias="rootMachineId")
    root_state_id: str | None = Field(default=None, alias="rootStateId")
    max_stack_depth: int = Field(alias="maxStackDepth")
    spin_loop_mode: str = Field(alias="spinLoopMode")
    context_inheritance_policy: str | None = Field(
        default=None,
        alias="contextInheritancePolicy",
    )
    runtime_limits: RuntimeLimits | None = Field(default=None, alias="runtimeLimits")
    persistent_store: dict[str, Any] | None = Field(
        default=None,
        alias="persistentStore",
    )


class Exposure(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_win_minor_units: int = Field(alias="maxWinMinorUnits")
    max_win_multiplier: int | None = Field(default=None, alias="maxWinMultiplier")
    cap_scope: str = Field(alias="capScope")
    enforce_cap: bool = Field(alias="enforceCap")
    validation_mode: str = Field(alias="validationMode")
    simulation_assisted: dict[str, Any] | None = Field(
        default=None,
        alias="simulationAssisted",
    )
    manual_attestation: dict[str, Any] | None = Field(
        default=None,
        alias="manualAttestation",
    )


class Determinism(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    rng_algorithm: str = Field(alias="rngAlgorithm")
    rng_algorithm_version: str | None = Field(default=None, alias="rngAlgorithmVersion")
    seed_derivation_policy: str | None = Field(
        default=None,
        alias="seedDerivationPolicy",
    )
    money_representation: str | None = Field(default=None, alias="moneyRepresentation")
    money_scale: int | None = Field(default=None, alias="moneyScale")


class Precedence(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    trigger_order: list[str] = Field(alias="triggerOrder")


class GameVersion(BaseModel):
    """Canonical game mathematics document (schema v1.0.0)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: str = Field(alias="schemaVersion")
    game_version: GameVersionMeta = Field(alias="gameVersion")
    metadata: Metadata
    game_config: GameConfig = Field(alias="gameConfig")
    symbols: dict[str, dict[str, Any]]
    reel_sets: dict[str, ReelSet] = Field(alias="reelSets")
    paytable: Paytable
    win_model: WinModel = Field(alias="winModel")
    bet_model: BetModel = Field(alias="betModel")
    plugins: dict[str, PluginRef]
    state_machines: dict[str, StateMachine] = Field(alias="stateMachines")
    session: SessionConfig
    exposure: Exposure
    determinism: Determinism
    precedence: Precedence
    extensions: dict[str, Any] = Field(default_factory=dict)
    rtp_category_registry: RtpCategoryRegistryDoc | None = Field(
        default=None,
        alias="rtpCategoryRegistry",
    )
    validation_metadata: dict[str, Any] | None = Field(
        default=None,
        alias="validationMetadata",
    )
    content_hash: str | None = Field(default=None, alias="contentHash")

    def to_json_dict(self, *, exclude_none: bool = True) -> dict[str, Any]:
        """Serialize to canonical JSON-compatible dict (camelCase keys)."""
        return self.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=exclude_none,
        )
