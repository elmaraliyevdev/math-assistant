"""Plugin and paytable domain types."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PluginRef(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    ref_id: str = Field(alias="refId")
    plugin_id: str = Field(alias="pluginId")
    plugin_version: str = Field(alias="pluginVersion")
    config_schema_version: str = Field(alias="configSchemaVersion")
    capabilities: list[str]


class ReelStrip(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    reel_index: int = Field(alias="reelIndex")
    symbols: list[str]
    weights: list[int] | None = None


class ReelSet(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    reels: list[ReelStrip]


class PaylineDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    index: int
    path: list[int]


class PaytableEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    symbol_id: str = Field(alias="symbolId")
    count: int
    multiplier: int | float


class Paytable(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    lines: list[PaylineDefinition] | None = None
    pays: list[PaytableEntry]


class WinModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: str
    direction: str | None = None
    scatter_pays_on_reels: bool | None = Field(default=None, alias="scatterPaysOnReels")
    highest_win_only_per_line: bool | None = Field(
        default=None,
        alias="highestWinOnlyPerLine",
    )


class RuntimeLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_steps_per_spin_chain: int | None = Field(
        default=None,
        alias="maxStepsPerSpinChain",
    )
    max_frames_per_chain: int | None = Field(default=None, alias="maxFramesPerChain")
    max_transitions_per_step: int | None = Field(
        default=None,
        alias="maxTransitionsPerStep",
    )
    max_respins_per_feature: int | None = Field(
        default=None,
        alias="maxRespinsPerFeature",
    )
    max_events_per_chain: int | None = Field(default=None, alias="maxEventsPerChain")
    max_wall_clock_ms_per_chain: int | None = Field(
        default=None,
        alias="maxWallClockMsPerChain",
    )


class RtpCategoryDef(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    label: str
    parent: str | None = None
    decomposition_group: str = Field(alias="decompositionGroup")
    description: str | None = None


class RtpCategoryRegistryDoc(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    extends: str | None = None
    categories: dict[str, RtpCategoryDef] = Field(default_factory=dict)
