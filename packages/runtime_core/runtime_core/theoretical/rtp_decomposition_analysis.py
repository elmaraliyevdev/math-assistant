"""Decomposition-aware RTP calibration recommendation analysis."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpDecompositionChart
from runtime_core.theoretical.discrepancy_severity import DiscrepancySeverity
from runtime_core.theoretical.models import CalibrationRecommendation, TheoreticalRtpResult

COMPONENTS: tuple[str, ...] = ("BASE", "FREE_SPINS", "HOLD_AND_WIN", "JACKPOT")

# Expected share of target RTP (min%, max%) per component for balanced slot math.
EXPECTED_SHARE_OF_TARGET: dict[str, tuple[float, float]] = {
    "BASE": (0.38, 0.55),
    "FREE_SPINS": (0.18, 0.38),
    "HOLD_AND_WIN": (0.05, 0.18),
    "JACKPOT": (0.02, 0.12),
}

HIGH_FREE_SPINS_SHARE_OF_TARGET = 0.30
JACKPOT_DOMINANCE_SHARE_OF_TOTAL = 0.35


@dataclass(frozen=True, slots=True)
class ComponentSnapshot:
    """Observed vs expected RTP contribution for one decomposition bucket."""

    component: str
    current_pp: float
    expected_min_pp: float
    expected_max_pp: float

    @property
    def deficit_pp(self) -> float:
        return max(0.0, self.expected_min_pp - self.current_pp)

    @property
    def surplus_pp(self) -> float:
        return max(0.0, self.current_pp - self.expected_max_pp)

    @property
    def is_underperforming(self) -> bool:
        return self.current_pp < self.expected_min_pp

    @property
    def is_dominant(self) -> bool:
        return self.current_pp > self.expected_max_pp


def resolve_decomposition_chart(
    *,
    theoretical: TheoreticalRtpResult,
    decomposition: RtpDecompositionChart | None = None,
) -> RtpDecompositionChart:
    """Use simulation decomposition when available, otherwise theoretical BASE-only view."""
    if decomposition is not None:
        return decomposition
    base_pp = round(theoretical.base_rtp * 100.0, 4)
    return RtpDecompositionChart(
        base=base_pp,
        free_spins=0.0,
        hold_and_win=0.0,
        jackpot=0.0,
        total_rtp=base_pp,
    )


def analyze_components(
    chart: RtpDecompositionChart,
    target_rtp: float,
) -> tuple[ComponentSnapshot, ...]:
    """Compare each RTP component against expected target ranges."""
    values = {
        "BASE": chart.base,
        "FREE_SPINS": chart.free_spins,
        "HOLD_AND_WIN": chart.hold_and_win,
        "JACKPOT": chart.jackpot,
    }
    snapshots: list[ComponentSnapshot] = []
    for component in COMPONENTS:
        min_share, max_share = EXPECTED_SHARE_OF_TARGET[component]
        snapshots.append(
            ComponentSnapshot(
                component=component,
                current_pp=values[component],
                expected_min_pp=round(target_rtp * min_share, 2),
                expected_max_pp=round(target_rtp * max_share, 2),
            ),
        )
    return tuple(snapshots)


def _component_map(
    snapshots: tuple[ComponentSnapshot, ...],
) -> dict[str, ComponentSnapshot]:
    return {item.component: item for item in snapshots}


def _impact_context(snapshot: ComponentSnapshot, impact_pp: float) -> str:
    return (
        f"{snapshot.component} RTP is {snapshot.current_pp:.2f}% "
        f"(expected {snapshot.expected_min_pp:.1f}–{snapshot.expected_max_pp:.1f}%). "
        f"Estimated {'+' if impact_pp >= 0 else ''}{impact_pp:.2f} percentage-point contribution."
    )


def _allocate_impact(
    gap_pp: float,
    snapshots: tuple[ComponentSnapshot, ...],
    *,
    use_deficit: bool = True,
) -> dict[str, float]:
    if use_deficit:
        weights = {s.component: s.deficit_pp for s in snapshots if s.is_underperforming}
    else:
        weights = {s.component: s.surplus_pp for s in snapshots if s.is_dominant}

    total_weight = sum(weights.values())
    if total_weight <= 0:
        return {}

    allocated: dict[str, float] = {}
    remaining = gap_pp
    items = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    for index, (component, weight) in enumerate(items):
        if index == len(items) - 1:
            share = remaining
        else:
            share = round(min(gap_pp * (weight / total_weight), remaining), 2)
            remaining = round(remaining - share, 2)
        allocated[component] = max(0.0, share)
    return allocated


def build_decomposition_raise_recommendations(
    *,
    chart: RtpDecompositionChart,
    target_rtp: float,
    gap_pp: float,
    severity: DiscrepancySeverity,
    game: GameVersion,
    theoretical: TheoreticalRtpResult,
) -> list[CalibrationRecommendation]:
    """Recommendations to raise RTP based on underperforming decomposition buckets."""
    snapshots = analyze_components(chart, target_rtp)
    by_component = _component_map(snapshots)
    free_spins = by_component["FREE_SPINS"]
    high_free_spins_share = (
        free_spins.current_pp >= target_rtp * HIGH_FREE_SPINS_SHARE_OF_TARGET
        or free_spins.is_dominant
    )

    underperforming = sorted(
        (item for item in snapshots if item.is_underperforming),
        key=lambda item: item.deficit_pp,
        reverse=True,
    )
    if not underperforming:
        return []

    impacts = _allocate_impact(gap_pp, snapshots, use_deficit=True)
    recommendations: list[CalibrationRecommendation] = []

    for snapshot in underperforming:
        impact = impacts.get(snapshot.component, 0.0)
        if impact <= 0:
            continue

        if snapshot.component == "BASE":
            recommendations.append(
                _base_raise_recommendation(
                    snapshot,
                    impact_pp=impact,
                    severity=severity,
                    game=game,
                ),
            )
        elif snapshot.component == "HOLD_AND_WIN":
            recommendations.append(
                _hold_and_win_raise_recommendation(
                    snapshot,
                    impact_pp=impact,
                    severity=severity,
                    game=game,
                ),
            )
        elif snapshot.component == "FREE_SPINS" and not high_free_spins_share:
            recommendations.append(
                _free_spins_raise_recommendation(
                    snapshot,
                    impact_pp=impact,
                    severity=severity,
                    game=game,
                ),
            )
        elif snapshot.component == "JACKPOT":
            recommendations.append(
                _jackpot_raise_recommendation(
                    snapshot,
                    impact_pp=impact,
                    severity=severity,
                ),
            )

    base_snapshot = by_component["BASE"]
    if high_free_spins_share and base_snapshot.is_underperforming:
        rebalance_impact = round(
            min(gap_pp * 0.2, base_snapshot.deficit_pp, free_spins.surplus_pp),
            2,
        )
        if rebalance_impact > 0:
            recommendations.append(
                CalibrationRecommendation(
                    severity="warning",
                    category="feature_rtp_rebalance",
                    action=(
                        "Feature RTP rebalancing: FREE_SPINS already contributes a large "
                        f"share ({free_spins.current_pp:.2f}%). Shift RTP from free-spin "
                        "awards into base paytable coverage rather than adding scatter "
                        "trigger weight."
                    ),
                    expectedRtpImpact=_impact_context(base_snapshot, rebalance_impact),
                    estimatedRtpContributionPp=rebalance_impact,
                    priority=75,
                    discrepancySeverity=severity.value,
                ),
            )

    if severity in {DiscrepancySeverity.CRITICAL, DiscrepancySeverity.MAJOR}:
        paytable_impact = round(
            min(gap_pp * 0.35, by_component["BASE"].deficit_pp or gap_pp * 0.35),
            2,
        )
        if paytable_impact > 0 and not any(
            rec.category == "paytable_redesign" for rec in recommendations
        ):
            recommendations.append(
                CalibrationRecommendation(
                    severity=(
                        "critical"
                        if severity == DiscrepancySeverity.CRITICAL
                        else "warning"
                    ),
                    category="paytable_redesign",
                    action=(
                        "Paytable redesign: expand line-pay coverage with lower-symbol "
                        "wins and mid-tier multipliers to lift BASE RTP toward the target "
                        "distribution."
                    ),
                    expectedRtpImpact=_impact_context(by_component["BASE"], paytable_impact),
                    estimatedRtpContributionPp=paytable_impact,
                    priority=88,
                    discrepancySeverity=severity.value,
                ),
            )

    return recommendations


def build_decomposition_lower_recommendations(
    *,
    chart: RtpDecompositionChart,
    target_rtp: float,
    gap_pp: float,
    severity: DiscrepancySeverity,
    game: GameVersion,
    theoretical: TheoreticalRtpResult,
) -> list[CalibrationRecommendation]:
    """Recommendations to lower RTP based on dominant decomposition buckets."""
    snapshots = analyze_components(chart, target_rtp)
    by_component = _component_map(snapshots)
    free_spins = by_component["FREE_SPINS"]
    total_pp = chart.total_rtp or (
        chart.base + chart.free_spins + chart.hold_and_win + chart.jackpot
    )
    high_free_spins_share = (
        free_spins.current_pp >= target_rtp * HIGH_FREE_SPINS_SHARE_OF_TARGET
        or (
            total_pp > 0
            and free_spins.current_pp / total_pp >= HIGH_FREE_SPINS_SHARE_OF_TARGET
        )
    )

    jackpot = by_component["JACKPOT"]
    jackpot_dominant = (
        jackpot.is_dominant
        or (total_pp > 0 and jackpot.current_pp / total_pp >= JACKPOT_DOMINANCE_SHARE_OF_TOTAL)
    )

    dominant = sorted(
        (item for item in snapshots if item.is_dominant or item.component == "JACKPOT"),
        key=lambda item: item.surplus_pp,
        reverse=True,
    )
    impacts = _allocate_impact(gap_pp, snapshots, use_deficit=False)
    recommendations: list[CalibrationRecommendation] = []

    if jackpot_dominant and jackpot.current_pp > 0:
        impact = impacts.get("JACKPOT", round(gap_pp * 0.4, 2))
        recommendations.append(
            CalibrationRecommendation(
                severity="warning",
                category="jackpot",
                action=(
                    "Reduce jackpot tier multipliers and tighten GRAND/MAJOR award "
                    f"tables. {jackpot.component} RTP is {jackpot.current_pp:.2f}% "
                    f"(expected {jackpot.expected_min_pp:.1f}–{jackpot.expected_max_pp:.1f}%)."
                ),
                expectedRtpImpact=_impact_context(jackpot, -impact),
                estimatedRtpContributionPp=impact,
                priority=85,
                discrepancySeverity=severity.value,
            ),
        )

    for snapshot in dominant:
        if snapshot.component == "JACKPOT" and jackpot_dominant:
            continue
        impact = impacts.get(snapshot.component, 0.0)
        if impact <= 0:
            continue

        if snapshot.component == "BASE":
            recommendations.append(
                _base_lower_recommendation(snapshot, impact_pp=impact, severity=severity, game=game),
            )
        elif snapshot.component == "FREE_SPINS":
            if high_free_spins_share:
                recommendations.append(
                    CalibrationRecommendation(
                        severity="warning",
                        category="feature_rtp_rebalance",
                        action=(
                            "Rebalance feature RTP: FREE_SPINS already represents a "
                            f"significant share ({free_spins.current_pp:.2f}%). Reduce "
                            "free-spin award values rather than lowering scatter trigger weight."
                        ),
                        expectedRtpImpact=_impact_context(snapshot, -impact),
                        estimatedRtpContributionPp=impact,
                        priority=70,
                        discrepancySeverity=severity.value,
                    ),
                )
            else:
                recommendations.append(
                    CalibrationRecommendation(
                        severity="warning",
                        category="scatter_frequency",
                        action=(
                            "Reduce scatter symbol weights on reel strips to lower "
                            "FREE_SPINS trigger rate."
                        ),
                        expectedRtpImpact=_impact_context(snapshot, -impact),
                        estimatedRtpContributionPp=impact,
                        priority=55,
                        discrepancySeverity=severity.value,
                    ),
                )
        elif snapshot.component == "HOLD_AND_WIN":
            recommendations.append(
                CalibrationRecommendation(
                    severity="warning",
                    category="hold_and_win",
                    action=(
                        "Tighten Hold & Win entry thresholds and reduce bonus symbol "
                        "density to lower feature RTP contribution."
                    ),
                    expectedRtpImpact=_impact_context(snapshot, -impact),
                    estimatedRtpContributionPp=impact,
                    priority=50,
                    discrepancySeverity=severity.value,
                ),
            )

    if not recommendations and severity in {
        DiscrepancySeverity.MINOR,
        DiscrepancySeverity.MODERATE,
    }:
        pays = game.paytable.pays
        if pays:
            top = max(pays, key=lambda entry: entry.multiplier)
            suggested = max(1, int(round(float(top.multiplier) * 0.95)))
            impact = _estimate_paytable_multiplier_impact_pp(
                theoretical,
                current_multiplier=float(top.multiplier),
                suggested_multiplier=float(suggested),
            )
            recommendations.append(
                CalibrationRecommendation(
                    severity="info",
                    category="paytable",
                    action=(
                        f"Trim {top.symbol_id} {top.count}OAK multiplier from "
                        f"{top.multiplier}x to {suggested}x."
                    ),
                    expectedRtpImpact=(
                        f"BASE RTP is {by_component['BASE'].current_pp:.2f}% "
                        f"(expected {by_component['BASE'].expected_min_pp:.1f}–"
                        f"{by_component['BASE'].expected_max_pp:.1f}%). "
                        f"Estimated -{impact:.2f} percentage-point contribution."
                    ),
                    estimatedRtpContributionPp=impact,
                    priority=20,
                    discrepancySeverity=severity.value,
                ),
            )

    return recommendations


def is_balanced_near_target(
    chart: RtpDecompositionChart,
    target_rtp: float,
    *,
    gap_pp: float,
) -> bool:
    """True when total RTP gap is minor and all components sit in expected bands."""
    if gap_pp > 2.0:
        return False
    snapshots = analyze_components(chart, target_rtp)
    return all(not item.is_underperforming and not item.is_dominant for item in snapshots)


def _base_raise_recommendation(
    snapshot: ComponentSnapshot,
    *,
    impact_pp: float,
    severity: DiscrepancySeverity,
    game: GameVersion,
) -> CalibrationRecommendation:
    actions = [
        "expand paytable coverage across lower-tier symbols",
        "add small line wins to improve hit frequency",
        "increase mid-tier multipliers before top-award changes",
    ]
    return CalibrationRecommendation(
        severity="warning" if severity != DiscrepancySeverity.MINOR else "info",
        category="base_rtp",
        action=(
            "Increase BASE RTP: " + ", ".join(actions) + "."
        ),
        expectedRtpImpact=_impact_context(snapshot, impact_pp),
        estimatedRtpContributionPp=impact_pp,
        priority=80,
        discrepancySeverity=severity.value,
    )


def _hold_and_win_raise_recommendation(
    snapshot: ComponentSnapshot,
    *,
    impact_pp: float,
    severity: DiscrepancySeverity,
    game: GameVersion,
) -> CalibrationRecommendation:
    threshold_hint = "Reduce Hold & Win entry thresholds"
    tiers = _jackpot_tiers(game)
    tier_hint = (
        f" and calibrate jackpot tiers ({', '.join(f'{k}={v}x' for k, v in tiers.items())})"
        if tiers
        else " and introduce calibrated jackpot tiers"
    )
    return CalibrationRecommendation(
        severity="warning",
        category="hold_and_win",
        action=(
            f"Introduce calibrated HOLD_AND_WIN contribution: {threshold_hint}{tier_hint}."
        ),
        expectedRtpImpact=_impact_context(snapshot, impact_pp),
        estimatedRtpContributionPp=impact_pp,
        priority=70,
        discrepancySeverity=severity.value,
    )


def _free_spins_raise_recommendation(
    snapshot: ComponentSnapshot,
    *,
    impact_pp: float,
    severity: DiscrepancySeverity,
    game: GameVersion,
) -> CalibrationRecommendation:
    award_text = _free_spin_award_hint(game, direction="raise")
    return CalibrationRecommendation(
        severity="info",
        category="feature_awards",
        action=f"Increase FREE_SPINS RTP: {award_text}",
        expectedRtpImpact=_impact_context(snapshot, impact_pp),
        estimatedRtpContributionPp=impact_pp,
        priority=60,
        discrepancySeverity=severity.value,
    )


def _jackpot_raise_recommendation(
    snapshot: ComponentSnapshot,
    *,
    impact_pp: float,
    severity: DiscrepancySeverity,
) -> CalibrationRecommendation:
    return CalibrationRecommendation(
        severity="info",
        category="jackpot",
        action=(
            "Increase JACKPOT RTP contribution by raising tier multipliers or "
            "entry frequency into jackpot-eligible states."
        ),
        expectedRtpImpact=_impact_context(snapshot, impact_pp),
        estimatedRtpContributionPp=impact_pp,
        priority=55,
        discrepancySeverity=severity.value,
    )


def _base_lower_recommendation(
    snapshot: ComponentSnapshot,
    *,
    impact_pp: float,
    severity: DiscrepancySeverity,
    game: GameVersion,
) -> CalibrationRecommendation:
    return CalibrationRecommendation(
        severity="info",
        category="base_rtp",
        action=(
            "Reduce BASE RTP by trimming line-pay multipliers across symbol tiers."
        ),
        expectedRtpImpact=_impact_context(snapshot, -impact_pp),
        estimatedRtpContributionPp=impact_pp,
        priority=45,
        discrepancySeverity=severity.value,
    )


def _jackpot_tiers(game: GameVersion) -> dict[str, int]:
    for machine in game.state_machines.values():
        for state in machine.states.values():
            raw = state.plugin_config.get("jackpotTiers")
            if isinstance(raw, dict) and raw:
                return {str(k): int(v) for k, v in raw.items()}
    return {}


def _free_spin_award_hint(game: GameVersion, *, direction: str) -> str:
    main = game.state_machines.get("main")
    if main is None:
        return (
            "increase free-spin award tables"
            if direction == "raise"
            else "reduce free-spin award tables"
        )
    base = main.states.get("BASE")
    if base is None:
        return "adjust free-spin award tables"
    raw = base.plugin_config.get("scatterTriggers", [])
    if isinstance(raw, list) and raw:
        spec = raw[0]
        if isinstance(spec, dict):
            award = spec.get("awardSpins") or spec.get("freeSpinsAward")
            if isinstance(award, int):
                if direction == "raise":
                    return f"raise trigger awards from {award} spins and review retriggers"
                return f"reduce trigger awards from {award} spins and tighten retriggers"
    return (
        "increase free-spin award tables"
        if direction == "raise"
        else "reduce free-spin award tables"
    )


def _estimate_paytable_multiplier_impact_pp(
    theoretical: TheoreticalRtpResult,
    *,
    current_multiplier: float,
    suggested_multiplier: float,
    top_symbol_weight: float = 0.35,
) -> float:
    if current_multiplier <= 0:
        return 0.0
    ratio_delta = suggested_multiplier / current_multiplier - 1.0
    return round(max(0.0, abs(theoretical.line_rtp * 100.0 * ratio_delta * top_symbol_weight)), 2)
