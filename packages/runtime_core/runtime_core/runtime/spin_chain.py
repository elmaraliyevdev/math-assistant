"""Spin chain request and result DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode, RuntimeEvent
from runtime_core.runtime.chain_metrics import ChainMetrics
from runtime_core.runtime.version import ENGINE_VERSION


class SimulationProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    profile_version: str = Field(alias="profileVersion")
    game_version_content_hash: str = Field(alias="gameVersionContentHash")


class SpinChainRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    game: GameVersion
    profile: SimulationProfile | None = None
    master_seed: bytes
    spin_chain_index: int = Field(alias="spinChainIndex")
    bet_minor_units: int = Field(default=0, alias="betMinorUnits")
    shard_index: int = Field(default=0, alias="shardIndex")
    simulation_run_id: str = Field(alias="simulationRunId")
    engine_version: str = Field(default="", alias="engineVersion")
    event_log_mode: EventLogMode = Field(
        default=EventLogMode.NONE,
        alias="eventLogMode",
    )

    def resolved_engine_version(self) -> str:
        return self.engine_version or ENGINE_VERSION


@dataclass(frozen=True, slots=True)
class LimitHit:
    code: str
    action: str


@dataclass(frozen=True, slots=True)
class ChainFault:
    code: str
    message: str
    frame_id: str = ""
    plugin_ref_id: str = ""


@dataclass(frozen=True, slots=True)
class AccumulatorDelta:
    capped_win_minor_units: int = 0
    uncapped_win_minor_units: int = 0
    exposure_truncation_count: int = 0
    exposure_truncated_minor_units: int = 0
    chain_fault_count: int = 0


@dataclass(frozen=True, slots=True)
class SpinChainResult:
    total_win_minor_units: int
    total_uncapped_win_minor_units: int
    total_truncated_minor_units: int
    total_bet_minor_units: int
    step_count: int
    frame_push_count: int
    exposure_cap_applied: bool
    limit_hit: LimitHit | None
    fault: ChainFault | None
    events: tuple[RuntimeEvent, ...]
    event_log_hash: str
    accumulator_delta: AccumulatorDelta
    chain_metrics: ChainMetrics = ChainMetrics.empty()
