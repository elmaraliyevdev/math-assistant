"""Mathematics API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MathematicsBaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    game_version_id: UUID = Field(alias="gameVersionId")
    reel_set_id: str | None = Field(default=None, alias="reelSetId")
    total_bet_minor_units: int | None = Field(default=None, alias="totalBetMinorUnits")
    simulation_id: UUID | None = Field(default=None, alias="simulationId")


class TheoreticalRtpResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    total_rtp: float = Field(alias="totalRtp")
    base_rtp: float = Field(alias="baseRtp")
    scatter_rtp: float = Field(alias="scatterRtp")
    line_rtp: float = Field(alias="lineRtp")
    outcome_count: int = Field(alias="outcomeCount")
    reel_set_id: str = Field(alias="reelSetId")


class FeatureProbabilityItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    trigger: str
    probability: float
    one_in_x: float | None = Field(default=None, alias="oneInX")


class TheoreticalAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    rtp: TheoreticalRtpResponse
    feature_probabilities: list[FeatureProbabilityItem] = Field(alias="featureProbabilities")
    engine_version: str = Field(alias="engineVersion")


class CalibrationResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

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


class DiscrepancyItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    metric: str
    theoretical: float | None = None
    simulated: float | None = None
    target: float | None = None
    delta: float
    status: str


class DiscrepancyAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[DiscrepancyItemResponse]
    summary: str


class CalibrationRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    severity: str
    category: str
    action: str
    expected_rtp_impact: str = Field(alias="expectedRtpImpact")


class CalibrateRequest(MathematicsBaseRequest):
    simulated_rtp: float | None = Field(default=None, alias="simulatedRtp")
    tolerance: float | None = None


class CalibrateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    theoretical_rtp: TheoreticalRtpResponse = Field(alias="theoreticalRtp")
    feature_probabilities: list[FeatureProbabilityItem] = Field(alias="featureProbabilities")
    calibration: CalibrationResultResponse
    discrepancy: DiscrepancyAnalysisResponse
    recommendations: list[CalibrationRecommendationResponse]
    engine_version: str = Field(alias="engineVersion")


class CertificationReportRequest(MathematicsBaseRequest):
    simulated_rtp: float | None = Field(default=None, alias="simulatedRtp")
    rtp_variance: float | None = Field(default=None, alias="rtpVariance")
    tolerance: float | None = None
    export_format: str | None = Field(default=None, alias="format", pattern="^(json|pdf)$")


class CertificationExposureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    max_win_minor_units: int = Field(alias="maxWinMinorUnits")
    max_win_multiplier: int | None = Field(default=None, alias="maxWinMultiplier")
    cap_scope: str = Field(alias="capScope")


class CertificationReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    game_version_id: UUID = Field(alias="gameVersionId")
    game_title: str = Field(alias="gameTitle")
    target_rtp: float | None = Field(default=None, alias="targetRtp")
    theoretical_rtp: TheoreticalRtpResponse = Field(alias="theoreticalRtp")
    simulated_rtp: float | None = Field(default=None, alias="simulatedRtp")
    rtp_variance: float | None = Field(default=None, alias="rtpVariance")
    feature_probabilities: list[FeatureProbabilityItem] = Field(alias="featureProbabilities")
    exposure: CertificationExposureResponse
    calibration: CalibrationResultResponse | None = None
    discrepancy: DiscrepancyAnalysisResponse | None = None
    recommendations: list[CalibrationRecommendationResponse] = Field(default_factory=list)
    engine_version: str = Field(alias="engineVersion")
