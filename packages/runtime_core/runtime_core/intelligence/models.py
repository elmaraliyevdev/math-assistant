"""Simulation intelligence domain models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    source: str
    path: str
    value: str
    spin_count: int = Field(alias="spinCount")


class IntelligenceConfidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    score: float
    label: str
    basis: str


class MetricExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    metric_id: str = Field(alias="metricId")
    label: str
    observed: str
    explanation: str
    confidence: IntelligenceConfidence
    evidence: tuple[EvidenceRef, ...]


class IntelligenceRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    id: str
    title: str
    reason: str
    recommendation: str
    confidence: IntelligenceConfidence
    evidence: tuple[EvidenceRef, ...]
    affected_reels: tuple[int, ...] = Field(default=(), alias="affectedReels")
    affected_symbols: tuple[str, ...] = Field(default=(), alias="affectedSymbols")
    expected_improvement: str = Field(alias="expectedImprovement")
    potential_rtp_influence: str = Field(default="Unknown", alias="potentialRtpInfluence")


class SymbolIntelligenceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    symbol_id: str = Field(alias="symbolId")
    occurrences: int
    expected_occurrences: float = Field(alias="expectedOccurrences")
    difference_percent: float = Field(alias="differencePercent")
    rtp_contribution_percent: float = Field(alias="rtpContributionPercent")
    average_spacing: float | None = Field(default=None, alias="averageSpacing")
    top_neighbours: tuple[str, ...] = Field(default=(), alias="topNeighbours")
    top_winning_combination: str | None = Field(default=None, alias="topWinningCombination")
    top_winning_combination_count: int = Field(default=0, alias="topWinningCombinationCount")
    health: str


class ScatterIntelligence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    observed_frequency: float = Field(alias="observedFrequency")
    expected_frequency: float = Field(alias="expectedFrequency")
    observed_spacing: float | None = Field(default=None, alias="observedSpacing")
    expected_spacing: float | None = Field(default=None, alias="expectedSpacing")
    clustering_score: float = Field(alias="clusteringScore")
    landing_heatmap: dict[str, int] = Field(default_factory=dict, alias="landingHeatmap")
    recommendation: IntelligenceRecommendation | None = None


class FeatureIntelligenceDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    feature_name: str = Field(alias="featureName")
    observed_frequency: float = Field(alias="observedFrequency")
    expected_frequency: float | None = Field(default=None, alias="expectedFrequency")
    average_entry_win_minor_units: float = Field(default=0.0, alias="averageEntryWinMinorUnits")
    average_duration: float | None = Field(default=None, alias="averageDuration")
    average_retriggers: float | None = Field(default=None, alias="averageRetriggers")
    rtp_contribution_percent: float = Field(alias="rtpContributionPercent")
    variance: float | None = None
    confidence: IntelligenceConfidence
    health: str


class PositionIntelligenceCell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    reel_index: int = Field(alias="reelIndex")
    position: int
    symbol_id: str = Field(alias="symbolId")
    landings: int
    winning_contribution: str = Field(alias="winningContribution")
    health: str


class ReelIntelligenceReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    reel_index: int = Field(alias="reelIndex")
    length: int
    entropy: float
    feature_density: float = Field(alias="featureDensity")
    wild_density: float = Field(alias="wildDensity")
    scatter_density: float = Field(alias="scatterDensity")
    winning_contribution_percent: float = Field(alias="winningContributionPercent")
    health: str
    rank: int


class ContributionSlice(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    id: str
    label: str
    rtp_percent: float = Field(alias="rtpPercent")


class DesignVsRealityItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    metric_id: str = Field(alias="metricId")
    label: str
    target: str
    observed: str
    status: str
    confidence: IntelligenceConfidence


class SimulationHeatmap(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    id: str
    label: str
    mode: str
    cells: dict[str, float]


class IntelligenceSnapshot(BaseModel):
    """Commutative counters collected during simulation execution."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    grid_observation_count: int = Field(default=0, alias="gridObservationCount")
    symbol_occurrence_counts: dict[str, int] = Field(
        default_factory=dict,
        alias="symbolOccurrenceCounts",
    )
    symbol_reel_counts: dict[str, dict[str, int]] = Field(
        default_factory=dict,
        alias="symbolReelCounts",
    )
    symbol_position_counts: dict[str, dict[str, int]] = Field(
        default_factory=dict,
        alias="symbolPositionCounts",
    )
    symbol_win_minor_units: dict[str, int] = Field(
        default_factory=dict,
        alias="symbolWinMinorUnits",
    )
    symbol_win_event_counts: dict[str, int] = Field(
        default_factory=dict,
        alias="symbolWinEventCounts",
    )
    reel_win_minor_units: dict[str, int] = Field(
        default_factory=dict,
        alias="reelWinMinorUnits",
    )
    winning_line_signatures: dict[str, int] = Field(
        default_factory=dict,
        alias="winningLineSignatures",
    )
    scatter_landings_by_reel: dict[str, int] = Field(
        default_factory=dict,
        alias="scatterLandingsByReel",
    )
    scatter_count_histogram: dict[str, int] = Field(
        default_factory=dict,
        alias="scatterCountHistogram",
    )
    wild_landings_by_reel: dict[str, int] = Field(
        default_factory=dict,
        alias="wildLandingsByReel",
    )
    feature_mode_grid_counts: dict[str, int] = Field(
        default_factory=dict,
        alias="featureModeGridCounts",
    )
    near_miss_count: int = Field(default=0, alias="nearMissCount")

    @classmethod
    def empty(cls) -> IntelligenceSnapshot:
        return cls()

    def merge(self, other: IntelligenceSnapshot) -> IntelligenceSnapshot:
        return IntelligenceSnapshot(
            grid_observation_count=self.grid_observation_count + other.grid_observation_count,
            symbol_occurrence_counts=_merge_counts(
                self.symbol_occurrence_counts,
                other.symbol_occurrence_counts,
            ),
            symbol_reel_counts=_merge_nested_counts(
                self.symbol_reel_counts,
                other.symbol_reel_counts,
            ),
            symbol_position_counts=_merge_nested_counts(
                self.symbol_position_counts,
                other.symbol_position_counts,
            ),
            symbol_win_minor_units=_merge_counts(
                self.symbol_win_minor_units,
                other.symbol_win_minor_units,
            ),
            symbol_win_event_counts=_merge_counts(
                self.symbol_win_event_counts,
                other.symbol_win_event_counts,
            ),
            reel_win_minor_units=_merge_counts(
                self.reel_win_minor_units,
                other.reel_win_minor_units,
            ),
            winning_line_signatures=_merge_counts(
                self.winning_line_signatures,
                other.winning_line_signatures,
            ),
            scatter_landings_by_reel=_merge_counts(
                self.scatter_landings_by_reel,
                other.scatter_landings_by_reel,
            ),
            scatter_count_histogram=_merge_counts(
                self.scatter_count_histogram,
                other.scatter_count_histogram,
            ),
            wild_landings_by_reel=_merge_counts(
                self.wild_landings_by_reel,
                other.wild_landings_by_reel,
            ),
            feature_mode_grid_counts=_merge_counts(
                self.feature_mode_grid_counts,
                other.feature_mode_grid_counts,
            ),
            near_miss_count=self.near_miss_count + other.near_miss_count,
        )


class SimulationIntelligenceReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    overview: str
    why_rtp_differs: tuple[str, ...] = Field(default=(), alias="whyRtpDiffers")
    symbol_profiles: tuple[SymbolIntelligenceProfile, ...] = Field(
        default=(),
        alias="symbolProfiles",
    )
    scatter_intelligence: ScatterIntelligence | None = Field(
        default=None,
        alias="scatterIntelligence",
    )
    feature_dashboards: tuple[FeatureIntelligenceDashboard, ...] = Field(
        default=(),
        alias="featureDashboards",
    )
    reel_reports: tuple[ReelIntelligenceReport, ...] = Field(
        default=(),
        alias="reelReports",
    )
    contribution_slices: tuple[ContributionSlice, ...] = Field(
        default=(),
        alias="contributionSlices",
    )
    design_vs_reality: tuple[DesignVsRealityItem, ...] = Field(
        default=(),
        alias="designVsReality",
    )
    heatmaps: tuple[SimulationHeatmap, ...] = ()
    position_highlights: tuple[PositionIntelligenceCell, ...] = Field(
        default=(),
        alias="positionHighlights",
    )
    unexpected_findings: tuple[str, ...] = Field(default=(), alias="unexpectedFindings")
    recommendations: tuple[IntelligenceRecommendation, ...] = ()
    metric_explanations: tuple[MetricExplanation, ...] = Field(
        default=(),
        alias="metricExplanations",
    )
    spin_count: int = Field(alias="spinCount")
    engine_version: str = Field(alias="engineVersion")


def _merge_counts(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    merged = dict(left)
    for key, value in right.items():
        merged[key] = merged.get(key, 0) + value
    return merged


def _merge_nested_counts(
    left: dict[str, dict[str, int]],
    right: dict[str, dict[str, int]],
) -> dict[str, dict[str, int]]:
    merged = {key: dict(value) for key, value in left.items()}
    for outer_key, inner in right.items():
        bucket = merged.setdefault(outer_key, {})
        for inner_key, value in inner.items():
            bucket[inner_key] = bucket.get(inner_key, 0) + value
    return merged
