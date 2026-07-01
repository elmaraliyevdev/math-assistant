"""Mathematical Engine result models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from runtime_core.intelligence.models import SimulationIntelligenceReport


class RTPResult(BaseModel):
    """Return-to-player metrics from aggregated simulation totals."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    rtp: float = Field(description="Capped RTP ratio: totalWin / totalBet")
    uncapped_rtp: float = Field(alias="uncappedRtp")
    total_bet_minor_units: int = Field(alias="totalBetMinorUnits")
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")
    uncapped_win_minor_units: int = Field(alias="uncappedWinMinorUnits")


class HitFrequencyResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    hit_frequency: float = Field(alias="hitFrequency")
    winning_spin_count: int = Field(alias="winningSpinCount")
    losing_spin_count: int = Field(alias="losingSpinCount")


class FeatureFrequencyResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    feature_name: str = Field(alias="featureName")
    trigger_count: int = Field(alias="triggerCount")
    frequency: float
    one_in_x: float | None = Field(alias="oneInX")


class JackpotFrequencyResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    jackpot_tier: str = Field(alias="jackpotTier")
    trigger_count: int = Field(alias="triggerCount")
    frequency: float
    one_in_x: float | None = Field(alias="oneInX")


class VolatilityResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    mean_win_minor_units: float = Field(alias="meanWinMinorUnits")
    variance: float
    standard_deviation: float = Field(alias="standardDeviation")
    coefficient_of_variation: float | None = Field(alias="coefficientOfVariation")


class ExposureAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    truncation_rate: float = Field(alias="truncationRate")
    total_truncated_minor_units: int = Field(alias="totalTruncatedMinorUnits")
    capped_rtp: float = Field(alias="cappedRtp")
    uncapped_rtp: float = Field(alias="uncappedRtp")
    rtp_difference: float = Field(alias="rtpDifference")


class WinDistributionBucket(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    label: str
    count: int
    percentage: float


class WinDistributionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    total_spins: int = Field(alias="totalSpins")
    bet_minor_units_per_spin: int = Field(alias="betMinorUnitsPerSpin")
    buckets: tuple[WinDistributionBucket, ...]


class ConfidenceIntervalResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    lower_bound: float = Field(alias="lowerBound")
    upper_bound: float = Field(alias="upperBound")
    confidence_level: float = Field(alias="confidenceLevel")


class RtpCategoryContribution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    rtp_category: str = Field(alias="rtpCategory")
    win_minor_units: int = Field(alias="winMinorUnits")
    rtp_share: float = Field(alias="rtpShare")


class RtpDecompositionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    total_rtp: float = Field(alias="totalRtp")
    categories: tuple[RtpCategoryContribution, ...]


class RtpValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    target_rtp: float = Field(alias="targetRtp")
    actual_rtp: float = Field(alias="actualRtp")
    difference: float
    tolerance: float
    within_tolerance: bool = Field(alias="withinTolerance")


class RtpDecompositionChart(BaseModel):
    """RTP shares on 0–100 percent scale for visualization."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    base: float = Field(default=0.0, alias="BASE")
    free_spins: float = Field(default=0.0, alias="FREE_SPINS")
    hold_and_win: float = Field(default=0.0, alias="HOLD_AND_WIN")
    jackpot: float = Field(default=0.0, alias="JACKPOT")
    total_rtp: float = Field(default=0.0, alias="totalRtp")


class FeatureValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    feature: str
    observed_frequency: float = Field(alias="observedFrequency")
    expected_frequency: float = Field(alias="expectedFrequency")
    difference: float
    status: str


class RecommendationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    severity: str
    title: str
    description: str


class MathematicsReport(BaseModel):
    """Aggregated mathematical analysis of one simulation run."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    rtp: RTPResult
    hit_frequency: HitFrequencyResult = Field(alias="hitFrequency")
    feature_frequencies: tuple[FeatureFrequencyResult, ...] = Field(
        alias="featureFrequencies",
    )
    jackpot_frequencies: tuple[JackpotFrequencyResult, ...] = Field(
        alias="jackpotFrequencies",
    )
    volatility: VolatilityResult
    exposure: ExposureAnalysisResult
    confidence_interval: ConfidenceIntervalResult = Field(alias="confidenceInterval")
    win_distribution: WinDistributionResult = Field(alias="winDistribution")
    rtp_decomposition: RtpDecompositionResult = Field(alias="rtpDecomposition")
    rtp_validation: RtpValidationResult | None = Field(default=None, alias="rtpValidation")
    rtp_decomposition_chart: RtpDecompositionChart = Field(
        default_factory=RtpDecompositionChart,
        alias="rtpDecompositionChart",
    )
    feature_validation: tuple[FeatureValidationResult, ...] = Field(
        default=(),
        alias="featureValidation",
    )
    recommendations: tuple[RecommendationResult, ...] = ()
    simulation_intelligence: SimulationIntelligenceReport | None = Field(
        default=None,
        alias="simulationIntelligence",
    )
    spin_count: int = Field(alias="spinCount")
    engine_version: str = Field(alias="engineVersion")
