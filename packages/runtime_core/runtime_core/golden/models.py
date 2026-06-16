"""Golden runtime validation data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RuntimeOverrides(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    hold_and_win_entry_min_count: int | None = Field(
        default=None,
        alias="holdAndWinEntryMinCount",
    )
    hold_and_win_trigger_symbol_count: int | None = Field(
        default=None,
        alias="holdAndWinTriggerSymbolCount",
    )


class GoldenRuntimeProfile(BaseModel):
    """Pinned execution inputs for one golden runtime validation chain."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    profile_version: str = Field(alias="profileVersion")
    mode: str
    engine_version: str = Field(alias="engineVersion")
    master_seed: str = Field(alias="masterSeed")
    spin_chain_index: int = Field(alias="spinChainIndex")
    shard_index: int = Field(default=0, alias="shardIndex")
    simulation_run_id: str = Field(alias="simulationRunId")
    bet_minor_units: int = Field(default=0, alias="betMinorUnits")
    event_log_mode: str = Field(alias="eventLogMode")
    game_version_content_hash: str = Field(alias="gameVersionContentHash")
    runtime_overrides: RuntimeOverrides | None = Field(
        default=None,
        alias="runtimeOverrides",
    )

    def master_seed_bytes(self) -> bytes:
        return bytes.fromhex(self.master_seed)


class ExpectedExposure(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    cap_applied: bool = Field(alias="capApplied")
    truncated_minor_units: int = Field(alias="truncatedMinorUnits")
    uncapped_win_minor_units: int = Field(alias="uncappedWinMinorUnits")
    truncation_count: int = Field(alias="truncationCount")


class ExpectedAccumulatorDelta(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    capped_win_minor_units: int = Field(alias="cappedWinMinorUnits")
    uncapped_win_minor_units: int = Field(alias="uncappedWinMinorUnits")
    exposure_truncation_count: int = Field(alias="exposureTruncationCount")
    exposure_truncated_minor_units: int = Field(alias="exposureTruncatedMinorUnits")
    chain_fault_count: int = Field(alias="chainFaultCount")


class ExpectedRuntimeOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    event_log_hash: str = Field(alias="eventLogHash")
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")
    total_bet_minor_units: int = Field(alias="totalBetMinorUnits")
    step_count: int = Field(alias="stepCount")
    frame_push_count: int = Field(alias="framePushCount")
    exposure: ExpectedExposure
    accumulator_delta: ExpectedAccumulatorDelta = Field(alias="accumulatorDelta")
    fault: str | None = None
    limit_hit: str | None = Field(default=None, alias="limitHit")


class ExpectedDeterminism(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    require_exact_engine_match: bool = Field(alias="requireExactEngineMatch")
    require_exact_event_log_hash: bool = Field(alias="requireExactEventLogHash")


class ExpectedBaseline(BaseModel):
    """Immutable runtime golden contract for one fixture chain."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    version: str
    locked: bool
    engine_version: str = Field(alias="engineVersion")
    runtime_outcome: ExpectedRuntimeOutcome = Field(alias="runtimeOutcome")
    determinism: ExpectedDeterminism


class GoldenRunOutcome(BaseModel):
    """Observed runtime outcome from one SessionExecutor invocation."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    engine_version: str = Field(alias="engineVersion")
    game_version_content_hash: str = Field(alias="gameVersionContentHash")
    event_log_hash: str = Field(alias="eventLogHash")
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")
    total_bet_minor_units: int = Field(alias="totalBetMinorUnits")
    step_count: int = Field(alias="stepCount")
    frame_push_count: int = Field(alias="framePushCount")
    exposure_cap_applied: bool = Field(alias="exposureCapApplied")
    total_uncapped_win_minor_units: int = Field(alias="totalUncappedWinMinorUnits")
    total_truncated_minor_units: int = Field(alias="totalTruncatedMinorUnits")
    chain_fault_count: int = Field(alias="chainFaultCount")
    exposure_truncation_count: int = Field(alias="exposureTruncationCount")
    exposure_truncated_minor_units: int = Field(alias="exposureTruncatedMinorUnits")
    capped_win_minor_units: int = Field(alias="cappedWinMinorUnits")
    uncapped_win_minor_units: int = Field(alias="uncappedWinMinorUnits")
    fault: str | None = None
    limit_hit: str | None = Field(default=None, alias="limitHit")


class GoldenDiff(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    field: str
    expected: str
    actual: str


class GoldenComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    fixture_id: str = Field(alias="fixtureId")
    passed: bool
    diffs: tuple[GoldenDiff, ...]


class GoldenValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    passed: bool
    engine_version: str = Field(alias="engineVersion")
    results: tuple[GoldenComparisonResult, ...]
