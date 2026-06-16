"""Simulation API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateSimulationRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "gameVersionId": "660e8400-e29b-41d4-a716-446655440001",
                    "spinCount": 1000,
                    "masterSeed": "cert-benchmark-seed",
                    "eventLogMode": "none",
                    "betMinorUnits": 100,
                },
            ],
        },
    )

    game_version_id: UUID = Field(alias="gameVersionId")
    spin_count: int = Field(alias="spinCount", ge=0)
    master_seed: str | None = Field(default=None, alias="masterSeed")
    event_log_mode: str = Field(default="none", alias="eventLogMode")
    bet_minor_units: int = Field(default=0, alias="betMinorUnits", ge=0)


class CreateSimulationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    status: str


class CancelSimulationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    status: str
    cancel_requested: bool = Field(alias="cancelRequested")


class SimulationProgress(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    completed_spins: int = Field(alias="completedSpins")
    percentage: float


class SimulationSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    game_version_id: UUID = Field(alias="gameVersionId")
    status: str
    spin_count: int = Field(alias="spinCount")
    completed_spin_count: int = Field(alias="completedSpinCount")
    created_at: datetime = Field(alias="createdAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    error_message: str | None = Field(default=None, alias="errorMessage")


class SimulationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[SimulationSummaryResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class SimulationDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    game_version_id: UUID = Field(alias="gameVersionId")
    status: str
    spin_count: int = Field(alias="spinCount")
    completed_spin_count: int = Field(alias="completedSpinCount")
    bet_minor_units: int = Field(alias="betMinorUnits")
    event_log_mode: str = Field(alias="eventLogMode")
    created_at: datetime = Field(alias="createdAt")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    cancel_requested: bool = Field(default=False, alias="cancelRequested")
    worker_id: str | None = Field(default=None, alias="workerId")
    error_message: str | None = Field(default=None, alias="errorMessage")
    progress: SimulationProgress
    total_shards: int = Field(default=0, alias="totalShards")
    completed_shards: int = Field(default=0, alias="completedShards")
    failed_shards: int = Field(default=0, alias="failedShards")
    progress_percentage: float = Field(default=0.0, alias="progressPercentage")
    distributed_execution: bool = Field(default=False, alias="distributedExecution")


class SimulationResultsSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    rtp: float
    uncapped_rtp: float = Field(alias="uncappedRtp")
    volatility: float
    hit_frequency: float = Field(alias="hitFrequency")


class SimulationResultsTotals(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    total_bet_minor_units: int = Field(alias="totalBetMinorUnits")
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")


class FeatureFrequencyItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    feature_name: str = Field(alias="featureName")
    trigger_count: int = Field(alias="triggerCount")
    frequency: float
    one_in_x: float | None = Field(default=None, alias="oneInX")


class JackpotFrequencyItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    jackpot_tier: str = Field(alias="jackpotTier")
    trigger_count: int = Field(alias="triggerCount")
    frequency: float
    one_in_x: float | None = Field(default=None, alias="oneInX")


class ExposureSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    truncation_rate: float = Field(alias="truncationRate")
    total_truncated_minor_units: int = Field(alias="totalTruncatedMinorUnits")
    capped_rtp: float = Field(alias="cappedRtp")
    uncapped_rtp: float = Field(alias="uncappedRtp")
    rtp_difference: float = Field(alias="rtpDifference")
    exposure_cap_applied: bool = Field(alias="exposureCapApplied")


class VolatilityMetricsSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    mean_win_minor_units: float = Field(alias="meanWinMinorUnits")
    variance: float
    standard_deviation: float = Field(alias="standardDeviation")
    coefficient_of_variation: float | None = Field(
        default=None,
        alias="coefficientOfVariation",
    )


class HitFrequencySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    hit_frequency: float = Field(alias="hitFrequency")
    winning_spin_count: int = Field(alias="winningSpinCount")
    losing_spin_count: int = Field(alias="losingSpinCount")


class WinDistributionBucketItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    label: str
    count: int
    percentage: float


class WinDistributionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    total_spins: int = Field(alias="totalSpins")
    bet_minor_units_per_spin: int = Field(alias="betMinorUnitsPerSpin")
    buckets: list[WinDistributionBucketItem]


class RtpCategoryContributionItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    rtp_category: str = Field(alias="rtpCategory")
    win_minor_units: int = Field(alias="winMinorUnits")
    rtp_share: float = Field(alias="rtpShare")


class RtpDecompositionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    total_rtp: float = Field(alias="totalRtp")
    categories: list[RtpCategoryContributionItem]


class RtpValidationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target_rtp: float = Field(alias="targetRtp")
    actual_rtp: float = Field(alias="actualRtp")
    difference: float
    tolerance: float
    within_tolerance: bool = Field(alias="withinTolerance")


class RtpDecompositionChartSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    base: float = Field(default=0.0, alias="BASE")
    free_spins: float = Field(default=0.0, alias="FREE_SPINS")
    hold_and_win: float = Field(default=0.0, alias="HOLD_AND_WIN")
    jackpot: float = Field(default=0.0, alias="JACKPOT")
    total_rtp: float = Field(default=0.0, alias="totalRtp")


class FeatureValidationItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    feature: str
    observed_frequency: float = Field(alias="observedFrequency")
    expected_frequency: float = Field(alias="expectedFrequency")
    difference: float
    status: str


class RecommendationItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    severity: str
    title: str
    description: str


class ConfidenceIntervalSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    rtp: float
    lower_bound: float = Field(alias="lowerBound")
    upper_bound: float = Field(alias="upperBound")
    confidence_level: float = Field(alias="confidenceLevel")


class SimulationResultsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    summary: SimulationResultsSummary
    totals: SimulationResultsTotals
    feature_frequencies: list[FeatureFrequencyItem] = Field(alias="featureFrequencies")
    jackpot_frequencies: list[JackpotFrequencyItem] = Field(alias="jackpotFrequencies")
    exposure: ExposureSummary
    rtp_decomposition: RtpDecompositionSummary = Field(alias="rtpDecomposition")
    rtp_validation: RtpValidationSummary | None = Field(default=None, alias="rtpValidation")
    rtp_decomposition_chart: RtpDecompositionChartSummary = Field(
        default_factory=RtpDecompositionChartSummary,
        alias="rtpDecompositionChart",
    )
    feature_validation: list[FeatureValidationItem] = Field(
        default_factory=list,
        alias="featureValidation",
    )
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    confidence_interval: ConfidenceIntervalSummary = Field(alias="confidenceInterval")
    win_distribution: WinDistributionSummary = Field(alias="winDistribution")
    volatility_metrics: VolatilityMetricsSummary = Field(alias="volatilityMetrics")
    hit_frequency: HitFrequencySummary = Field(alias="hitFrequency")
    engine_version: str = Field(alias="engineVersion")
    game_version_content_hash: str = Field(alias="gameVersionContentHash")
    certification_notice: str = Field(alias="certificationNotice")


class SimulationCompareEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    game_name: str | None = Field(default=None, alias="gameName")
    game_version_label: str | None = Field(default=None, alias="gameVersionLabel")
    detail: SimulationDetailResponse
    results: SimulationResultsResponse
    runtime_duration_ms: int | None = Field(default=None, alias="runtimeDurationMs")


class ComparisonMetricItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    value: float


class ComparisonConfidenceIntervalItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    lower_bound: float = Field(alias="lowerBound")
    upper_bound: float = Field(alias="upperBound")
    confidence_level: float = Field(alias="confidenceLevel")


class ComparisonFeatureFrequencyItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    feature_name: str = Field(alias="featureName")
    frequency: float


class ComparisonRtpDecompositionItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    base: float = Field(alias="BASE")
    free_spins: float = Field(alias="FREE_SPINS")
    hold_and_win: float = Field(alias="HOLD_AND_WIN")
    jackpot: float = Field(alias="JACKPOT")
    total_rtp: float = Field(alias="totalRtp")


class SimulationComparisonMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    rtp: list[ComparisonMetricItem]
    volatility: list[ComparisonMetricItem]
    hit_frequency: list[ComparisonMetricItem] = Field(alias="hitFrequency")
    confidence_intervals: list[ComparisonConfidenceIntervalItem] = Field(
        alias="confidenceIntervals",
    )
    feature_frequency: list[ComparisonFeatureFrequencyItem] = Field(
        alias="featureFrequency",
    )
    rtp_decomposition: list[ComparisonRtpDecompositionItem] = Field(
        alias="rtpDecomposition",
    )


class SimulationCompareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulations: list[SimulationCompareEntry]
    comparison: SimulationComparisonMetrics


class SimulationThroughputResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    spins_per_second: float = Field(alias="spinsPerSecond")
    sample_count: int = Field(alias="sampleCount")
    source: str


class CreateSimulationNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    content: str = Field(min_length=1, max_length=4000)


class SimulationNoteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    simulation_id: UUID = Field(alias="simulationId")
    author_id: UUID = Field(alias="authorId")
    content: str
    created_at: datetime = Field(alias="createdAt")


class SimulationNoteListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[SimulationNoteResponse]
