"""Theoretical mathematics and calibration result models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TheoreticalRtpResult(BaseModel):
    """Exact base-game RTP from reel-strip enumeration."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    total_rtp: float = Field(alias="totalRtp")
    base_rtp: float = Field(alias="baseRtp")
    scatter_rtp: float = Field(alias="scatterRtp")
    line_rtp: float = Field(alias="lineRtp")
    outcome_count: int = Field(alias="outcomeCount")
    reel_set_id: str = Field(alias="reelSetId")


class FeatureProbability(BaseModel):
    """Theoretical trigger probability for a feature or jackpot tier."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    trigger: str
    probability: float
    one_in_x: float | None = Field(default=None, alias="oneInX")


class CalibrationResult(BaseModel):
    """Comparison of target, theoretical, and simulated RTP."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    target_rtp: float | None = Field(default=None, alias="targetRtp")
    theoretical_rtp: float = Field(alias="theoreticalRtp")
    simulated_rtp: float | None = Field(default=None, alias="simulatedRtp")
    target_delta: float | None = Field(default=None, alias="targetDelta")
    theory_vs_simulation_delta: float | None = Field(
        default=None,
        alias="theoryVsSimulationDelta",
    )
    within_tolerance: bool | None = Field(default=None, alias="withinTolerance")
    tolerance: float | None = None


class CalibrationRecommendation(BaseModel):
    """Actionable tuning suggestion with expected RTP impact."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    severity: str
    category: str
    action: str
    expected_rtp_impact: str = Field(alias="expectedRtpImpact")


class DiscrepancyItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    metric: str
    theoretical: float | None = None
    simulated: float | None = None
    target: float | None = None
    delta: float
    status: str


class DiscrepancyAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    items: tuple[DiscrepancyItem, ...]
    summary: str


class CertificationExposureStats(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    max_win_minor_units: int = Field(alias="maxWinMinorUnits")
    max_win_multiplier: int | None = Field(default=None, alias="maxWinMultiplier")
    cap_scope: str = Field(alias="capScope")


class CertificationReport(BaseModel):
    """Certification-ready mathematics summary."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    game_version_id: str = Field(alias="gameVersionId")
    game_title: str = Field(alias="gameTitle")
    target_rtp: float | None = Field(default=None, alias="targetRtp")
    theoretical_rtp: TheoreticalRtpResult = Field(alias="theoreticalRtp")
    simulated_rtp: float | None = Field(default=None, alias="simulatedRtp")
    rtp_variance: float | None = Field(default=None, alias="rtpVariance")
    feature_probabilities: tuple[FeatureProbability, ...] = Field(
        alias="featureProbabilities",
    )
    exposure: CertificationExposureStats
    calibration: CalibrationResult | None = None
    discrepancy: DiscrepancyAnalysis | None = None
    recommendations: tuple[CalibrationRecommendation, ...] = ()
    engine_version: str = Field(alias="engineVersion")


class TheoreticalAnalysis(BaseModel):
    """Combined theoretical RTP and feature probability report."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    rtp: TheoreticalRtpResult
    feature_probabilities: tuple[FeatureProbability, ...] = Field(
        alias="featureProbabilities",
    )
    engine_version: str = Field(alias="engineVersion")
