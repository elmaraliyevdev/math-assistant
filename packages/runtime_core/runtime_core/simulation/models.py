"""Simulation Engine data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.version import ENGINE_VERSION


class SimulationProfile(BaseModel):
    """Monte Carlo simulation run configuration (non-canonical)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    profile_version: str = Field(default="1.0.0", alias="profileVersion")
    spin_count: int = Field(alias="spinCount", ge=0)
    shard_count: int = Field(default=1, alias="shardCount", ge=1)
    master_seed: bytes = Field(alias="masterSeed")
    simulation_run_id: str = Field(alias="simulationRunId")
    event_log_mode: EventLogMode = Field(
        default=EventLogMode.NONE,
        alias="eventLogMode",
    )
    sample_events: int = Field(default=0, alias="sampleEvents", ge=0)
    max_faults: int | None = Field(default=None, alias="maxFaults")
    bet_minor_units: int = Field(default=0, alias="betMinorUnits", ge=0)
    engine_version: str = Field(default="", alias="engineVersion")

    @field_validator("master_seed", mode="before")
    @classmethod
    def _coerce_master_seed(cls, value: object) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("0x"):
                return bytes.fromhex(text[2:])
            try:
                return bytes.fromhex(text)
            except ValueError:
                return text.encode("utf-8")
        msg = "masterSeed must be bytes or hex string"
        raise TypeError(msg)

    def resolved_engine_version(self) -> str:
        return self.engine_version or ENGINE_VERSION


class SimulationResult(BaseModel):
    """Aggregated Monte Carlo simulation outcome."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    spin_count: int = Field(alias="spinCount")
    shard_count: int = Field(alias="shardCount")
    elapsed_time_ms: int = Field(alias="elapsedTimeMs")
    total_bet_minor_units: int = Field(alias="totalBetMinorUnits")
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")
    uncapped_win_minor_units: int = Field(alias="uncappedWinMinorUnits")
    exposure_truncation_count: int = Field(alias="exposureTruncationCount")
    exposure_truncated_minor_units: int = Field(alias="exposureTruncatedMinorUnits")
    chain_fault_count: int = Field(alias="chainFaultCount")
    limit_hit_count: int = Field(alias="limitHitCount")
    feature_trigger_counts: dict[str, int] = Field(alias="featureTriggerCounts")
    jackpot_counts: dict[str, int] = Field(alias="jackpotCounts")
    win_by_rtp_category_minor_units: dict[str, int] = Field(
        default_factory=dict,
        alias="winByRtpCategoryMinorUnits",
    )
    nested_feature_entries: int = Field(default=0, alias="nestedFeatureEntries")
    event_sample_count: int = Field(alias="eventSampleCount")
    engine_version: str = Field(alias="engineVersion")
