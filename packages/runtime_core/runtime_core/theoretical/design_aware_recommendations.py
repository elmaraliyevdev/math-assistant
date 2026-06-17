"""Design-aware filtering and certification readiness for calibration guidance."""

from __future__ import annotations

import math
import re

from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.design_intent import DesignIntent, detect_design_intent
from runtime_core.theoretical.models import (
    CalibrationRecommendation,
    CalibrationResult,
    CertificationReadinessSummary,
    TheoreticalRtpResult,
)

_INTRODUCE_PATTERN = re.compile(r"\bintroduce\b", re.IGNORECASE)
_COMPONENT_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("FREE_SPINS", "has_free_spins"),
    ("HOLD_AND_WIN", "has_hold_and_win"),
    ("HOLD & WIN", "has_hold_and_win"),
    ("JACKPOT", "has_jackpot"),
)

_VOLATILITY_CLASS_ORDER = ("low", "medium", "high")

_CATEGORY_VOLATILITY: dict[str, tuple[str, float]] = {
    "base_rtp": ("neutral", 0.08),
    "paytable_redesign": ("low_increase", 0.18),
    "paytable": ("moderate_increase", 0.42),
    "feature_awards": ("moderate_increase", 0.28),
    "scatter_frequency": ("moderate_increase", 0.32),
    "feature_rtp_rebalance": ("low_increase", 0.12),
    "hold_and_win": ("moderate_increase", 0.35),
    "jackpot": ("high_increase", 0.55),
    "simulation_validation": ("neutral", 0.0),
    "certification": ("neutral", 0.0),
    "status": ("neutral", 0.0),
}


def apply_design_aware_constraints(
    recommendations: tuple[CalibrationRecommendation, ...],
    *,
    game: GameVersion,
    theoretical: TheoreticalRtpResult,
    allow_volatility_class_change: bool = False,
) -> tuple[CalibrationRecommendation, ...]:
    """Filter and enrich recommendations to respect canonical design intent."""
    intent = detect_design_intent(game)
    filtered: list[CalibrationRecommendation] = []

    for recommendation in recommendations:
        if not _recommendation_allowed(
            recommendation,
            intent=intent,
            allow_volatility_class_change=allow_volatility_class_change,
        ):
            continue
        filtered.append(
            _enrich_recommendation(
                recommendation,
                intent=intent,
                theoretical=theoretical,
            ),
        )

    return tuple(filtered)


def build_certification_readiness_summary(
    calibration: CalibrationResult,
    recommendations: tuple[CalibrationRecommendation, ...],
) -> CertificationReadinessSummary:
    """Summarize certification blockers and remaining calibration work."""
    blocking_issues: list[str] = []
    if calibration.certification_status == "certification_blocked":
        gap = calibration.rtp_gap_pp or 0.0
        threshold = calibration.certification_block_threshold_pp or 25.0
        blocking_issues.append(
            f"RTP gap {gap:.2f} pp exceeds certification block threshold ({threshold:.0f} pp).",
        )
    if calibration.within_tolerance is False:
        blocking_issues.append("Observed RTP is outside the configured tolerance band.")
    if (
        calibration.theory_vs_simulation_delta is not None
        and abs(calibration.theory_vs_simulation_delta) > 0.5
    ):
        blocking_issues.append(
            "Theory vs simulation delta exceeds 0.50 pp — validate simulation inputs.",
        )

    actionable = [
        rec
        for rec in recommendations
        if rec.estimated_rtp_contribution_pp > 0
        and rec.category not in {"certification", "status", "simulation_validation"}
    ]
    required_actions = tuple(rec.action for rec in actionable[:5])

    gap_pp = calibration.rtp_gap_pp or 0.0
    if gap_pp <= 0.01 and not blocking_issues:
        iterations = 0
    else:
        total_impact = sum(rec.estimated_rtp_contribution_pp for rec in actionable)
        if total_impact <= 0:
            iterations = max(3, int(math.ceil(gap_pp / 5.0)) + 1)
        else:
            iterations = max(1, int(math.ceil(gap_pp / (total_impact * 0.65))))

    status = calibration.certification_status
    if status is None:
        if gap_pp <= 2.0 and not blocking_issues:
            status = "cleared"
        elif gap_pp > (calibration.certification_block_threshold_pp or 25.0):
            status = "certification_blocked"
        else:
            status = "review_required"

    return CertificationReadinessSummary(
        certificationStatus=status,
        blockingIssues=tuple(blocking_issues),
        requiredActions=required_actions,
        estimatedIterationsRemaining=iterations,
    )


def _recommendation_allowed(
    recommendation: CalibrationRecommendation,
    *,
    intent: DesignIntent,
    allow_volatility_class_change: bool,
) -> bool:
    if recommendation.category in {"certification", "status", "simulation_validation"}:
        return True

    if not _feature_presence_allowed(recommendation, intent):
        return False

    volatility_level, volatility_score = _estimate_volatility(recommendation)
    if not allow_volatility_class_change and _violates_volatility_target(
        intent.volatility_target,
        volatility_level,
        volatility_score,
    ):
        return False

    exposure_level = _estimate_exposure_impact(recommendation, intent)
    if intent.enforce_exposure_cap and exposure_level == "exceeds_cap_risk":
        return False

    return True


def _feature_presence_allowed(
    recommendation: CalibrationRecommendation,
    intent: DesignIntent,
) -> bool:
    action = recommendation.action
    category = recommendation.category

    if category == "hold_and_win" and not intent.has_hold_and_win:
        return False
    if category in {"feature_awards", "scatter_frequency"} and not intent.has_free_spins:
        return False
    if category == "jackpot" and not intent.has_jackpot:
        return False
    if category == "feature_rtp_rebalance" and "FREE_SPINS" in action:
        return intent.has_free_spins

    if _INTRODUCE_PATTERN.search(action):
        for keyword, attr in _COMPONENT_KEYWORDS:
            if keyword in action and not getattr(intent, attr):
                return False

    for keyword, attr in _COMPONENT_KEYWORDS:
        if keyword in action and category not in {"base_rtp", "paytable_redesign", "paytable"}:
            if not getattr(intent, attr) and _INTRODUCE_PATTERN.search(action):
                return False

    return True


def _enrich_recommendation(
    recommendation: CalibrationRecommendation,
    *,
    intent: DesignIntent,
    theoretical: TheoreticalRtpResult,
) -> CalibrationRecommendation:
    volatility_level, _ = _estimate_volatility(recommendation)
    exposure_level = _estimate_exposure_impact(recommendation, intent)
    volatility_text = _format_volatility_impact(volatility_level, intent.volatility_target)
    exposure_text = _format_exposure_impact(exposure_level, intent)

    impact_parts = [recommendation.expected_rtp_impact]
    if volatility_text:
        impact_parts.append(volatility_text)
    if exposure_text:
        impact_parts.append(exposure_text)

    return recommendation.model_copy(
        update={
            "expected_rtp_impact": " ".join(impact_parts),
            "estimated_volatility_impact": volatility_text,
            "exposure_impact": exposure_text,
        },
    )


def _estimate_volatility(
    recommendation: CalibrationRecommendation,
) -> tuple[str, float]:
    level, score = _CATEGORY_VOLATILITY.get(
        recommendation.category,
        ("neutral", 0.1),
    )
    action_lower = recommendation.action.lower()
    if "top-award" in action_lower or "jackpot tier" in action_lower:
        return "high_increase", max(score, 0.55)
    if "lower-symbol" in action_lower or "mid-tier" in action_lower:
        return "low_increase", min(score, 0.15)
    if "multiplier from" in action_lower:
        return "moderate_increase", max(score, 0.4)
    return level, score


def _violates_volatility_target(
    volatility_target: str | None,
    impact_level: str,
    impact_score: float,
) -> bool:
    if volatility_target is None:
        return False
    target_class = _normalize_volatility_class(volatility_target)
    if target_class != "low":
        return False
    if impact_level == "high_increase":
        return True
    return impact_level == "moderate_increase" and impact_score >= 0.35


def _normalize_volatility_class(volatility_target: str) -> str:
    normalized = volatility_target.strip().lower()
    if "low" in normalized:
        return "low"
    if "high" in normalized:
        return "high"
    return "medium"


def _format_volatility_impact(level: str, volatility_target: str | None) -> str:
    label = level.replace("_", " ")
    if volatility_target:
        return (
            f"Estimated volatility impact: {label} "
            f"(design target: {volatility_target})."
        )
    return f"Estimated volatility impact: {label}."


def _estimate_exposure_impact(
    recommendation: CalibrationRecommendation,
    intent: DesignIntent,
) -> str:
    action_lower = recommendation.action.lower()
    if recommendation.category == "jackpot" or "jackpot tier" in action_lower:
        if "reduce" in action_lower or "tighten" in action_lower:
            return "within_cap"
        return "exceeds_cap_risk" if intent.enforce_exposure_cap else "approaching_cap"
    if recommendation.category == "paytable" and "multiplier from" in action_lower:
        if intent.enforce_exposure_cap and intent.max_win_multiplier is not None:
            return "approaching_cap"
        return "within_cap"
    if "lower-symbol" in action_lower or "trim" in action_lower:
        return "within_cap"
    if recommendation.category in {"base_rtp", "paytable_redesign"}:
        return "within_cap"
    if intent.enforce_exposure_cap and recommendation.category in {
        "hold_and_win",
        "feature_awards",
    }:
        return "approaching_cap"
    return "within_cap"


def _format_exposure_impact(level: str, intent: DesignIntent) -> str:
    cap = intent.max_win_minor_units
    multiplier = intent.max_win_multiplier
    if level == "within_cap":
        return f"Exposure: within cap ({cap:,} minor units)."
    if level == "approaching_cap":
        suffix = f", {multiplier}x bet" if multiplier is not None else ""
        return f"Exposure: approaches cap ({cap:,} minor units{suffix})."
    suffix = f", {multiplier}x bet" if multiplier is not None else ""
    return (
        f"Exposure: risks exceeding cap ({cap:,} minor units{suffix}) — "
        "prefer lower-tier paytable adjustments."
    )
