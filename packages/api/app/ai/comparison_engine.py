"""Comparison and game-design grounded explanations."""

from __future__ import annotations

import uuid

from app.ai.context_builder import (
    ComparisonArtifactContext,
    GameVersionArtifactContext,
    extract_jackpot_tiers,
    extract_paytable_summary,
    extract_rtp_target,
    extract_scatter_triggers,
    exposure_from_canonical,
)
from app.ai.grounding import cite, format_percent_ratio, grounded_sentence, unique_citations
from app.ai.prompt_builder import build_comparison_sections, build_game_design_sections, compose_narrative


def explain_comparison(context: ComparisonArtifactContext) -> dict:
    comparison = context.comparison
    citations: list = []

    rtp_by_sim = {
        item.simulation_id: item.value for item in comparison.comparison.rtp
    }
    vol_by_sim = {
        item.simulation_id: item.value for item in comparison.comparison.volatility
    }

    if len(rtp_by_sim) < 2:
        rtp_diff_text = "Insufficient simulations for RTP comparison."
    else:
        sim_ids = list(rtp_by_sim.keys())
        high_sim = max(sim_ids, key=lambda sim_id: rtp_by_sim[sim_id])
        low_sim = min(sim_ids, key=lambda sim_id: rtp_by_sim[sim_id])
        high_rtp = rtp_by_sim[high_sim]
        low_rtp = rtp_by_sim[low_sim]
        delta = (high_rtp - low_rtp) * 100
        rtp_citation_high = cite(
            label=f"Simulation #{str(high_sim)[:8]}",
            source="comparison_report",
            path="comparison.rtp",
            value=round(high_rtp, 6),
        )
        rtp_citation_low = cite(
            label=f"Simulation #{str(low_sim)[:8]}",
            source="comparison_report",
            path="comparison.rtp",
            value=round(low_rtp, 6),
        )
        rtp_diff_text = grounded_sentence(
            (
                f"RTP ranges from {format_percent_ratio(low_rtp)} "
                f"(simulation {str(low_sim)[:8]}) to {format_percent_ratio(high_rtp)} "
                f"(simulation {str(high_sim)[:8]}), a spread of {delta:.2f} percentage points."
            ),
            rtp_citation_low,
            rtp_citation_high,
        )
        citations.extend([rtp_citation_low, rtp_citation_high])

    feature_map: dict[str, dict[uuid.UUID, float]] = {}
    for item in comparison.comparison.feature_frequency:
        feature_map.setdefault(item.feature_name, {})[item.simulation_id] = item.frequency

    feature_lines: list[str] = []
    for feature_name, frequencies in sorted(feature_map.items()):
        if len(frequencies) < 2:
            continue
        values = list(frequencies.items())
        max_sim, max_freq = max(values, key=lambda pair: pair[1])
        min_sim, min_freq = min(values, key=lambda pair: pair[1])
        feature_citation = cite(
            label="Comparison Report",
            source="comparison_report",
            path=f"comparison.featureFrequency.{feature_name}",
            value=round(max_freq - min_freq, 6),
        )
        feature_lines.append(
            grounded_sentence(
                (
                    f"{feature_name} frequency varies from {min_freq * 100:.4f}% "
                    f"({str(min_sim)[:8]}) to {max_freq * 100:.4f}% ({str(max_sim)[:8]})."
                ),
                feature_citation,
            ),
        )
        citations.append(feature_citation)
    feature_diff_text = (
        " ".join(feature_lines)
        if feature_lines
        else "No feature frequency differences were present in the comparison report."
    )

    target_text = _closest_to_target(comparison, citations)

    vol_values = list(vol_by_sim.items())
    if len(vol_values) >= 2:
        high_vol_sim, high_vol = max(vol_values, key=lambda pair: pair[1])
        low_vol_sim, low_vol = min(vol_values, key=lambda pair: pair[1])
        tradeoff_text = grounded_sentence(
            (
                f"Higher RTP simulation {str(high_vol_sim)[:8]} has volatility "
                f"{vol_by_sim.get(high_vol_sim, 0):.4f}; lower RTP simulation "
                f"{str(low_vol_sim)[:8]} has volatility {low_vol:.4f}. "
                "Increasing RTP often coincides with higher volatility in these runs."
            ),
            cite(
                label="Comparison Report",
                source="comparison_report",
                path="comparison.volatility",
                value=round(high_vol - low_vol, 6),
            ),
        )
    else:
        tradeoff_text = "Insufficient data for volatility vs RTP trade-off analysis."

    unique = unique_citations(*citations)
    sections = build_comparison_sections(
        rtp_diff_text=rtp_diff_text,
        feature_diff_text=feature_diff_text,
        target_text=target_text,
        tradeoff_text=tradeoff_text,
        citations=unique,
    )
    return {
        "simulationIds": [str(entry.simulation_id) for entry in comparison.simulations],
        "content": compose_narrative(sections),
        "sections": sections,
        "citations": [citation.to_dict() for citation in unique],
    }


def explain_game_version(context: GameVersionArtifactContext) -> dict:
    canonical = context.canonical_json
    citations: list = []

    triggers = extract_scatter_triggers(canonical)
    jackpots = extract_jackpot_tiers(canonical)
    pays = extract_paytable_summary(canonical)
    exposure = exposure_from_canonical(canonical)

    trigger_names = sorted(
        {str(item.get("emitTrigger", "")) for item in triggers if item.get("emitTrigger")},
    )
    structure_text = grounded_sentence(
        (
            f"Game '{context.game_title}' defines {len(triggers)} trigger rule(s) "
            f"covering features: {', '.join(trigger_names) or 'none'}."
        ),
        cite(
            label="Game Canonical JSON",
            source="game_canonical_json",
            path="stateMachines.main.states",
        ),
    )
    if jackpots:
        structure_text += " " + grounded_sentence(
            f"Jackpot tiers configured: {', '.join(f'{k}={v}x' for k, v in jackpots.items())}.",
            cite(
                label="Game Canonical JSON",
                source="game_canonical_json",
                path="stateMachines.hold_and_win.states.HAW_RESPINS.pluginConfig.jackpotTiers",
            ),
        )

    target = extract_rtp_target(canonical)
    if target is not None:
        rtp_text = grounded_sentence(
            f"Configured RTP target is {target:.2f}%.",
            cite(
                label="Game Canonical JSON",
                source="game_canonical_json",
                path="metadata.rtpTarget.percent",
                value=target,
            ),
        )
        citations.append(
            cite(
                label="Game Canonical JSON",
                source="game_canonical_json",
                path="metadata.rtpTarget.percent",
                value=target,
            ),
        )
    else:
        rtp_text = "No RTP target is configured in canonical metadata."

    theory = context.theoretical
    trigger_lines: list[str] = []
    for feature in theory.feature_probabilities:
        trigger_citation = cite(
            label="Theoretical Analysis",
            source="theoretical_analysis",
            path=f"featureProbabilities.{feature.trigger}",
            value=round(feature.probability, 8),
        )
        one_in = f" (1 in {feature.one_in_x})" if feature.one_in_x else ""
        trigger_lines.append(
            grounded_sentence(
                f"{feature.trigger} theoretical trigger probability is "
                f"{feature.probability * 100:.4f}%{one_in}.",
                trigger_citation,
            ),
        )
        citations.append(trigger_citation)
    trigger_text = (
        " ".join(trigger_lines)
        if trigger_lines
        else "No theoretical feature probabilities are available in stored analysis."
    )

    theory_pct = theory.rtp.total_rtp * 100
    max_win = exposure.get("maxWinMinorUnits")
    risk_text = grounded_sentence(
        (
            f"Theoretical base RTP is {theory_pct:.2f}% with "
            f"{len(pays)} paytable entries and max win cap "
            f"{max_win if max_win is not None else 'not set'} minor units."
        ),
        cite(
            label="Theoretical Analysis",
            source="theoretical_analysis",
            path="rtp.totalRtp",
            value=round(theory_pct, 4),
        ),
        cite(
            label="Game Canonical JSON",
            source="game_canonical_json",
            path="exposure.maxWinMinorUnits",
            value=max_win if isinstance(max_win, (int, float)) else None,
        ),
    )

    unique = unique_citations(*citations)
    sections = build_game_design_sections(
        structure_text=structure_text,
        rtp_text=rtp_text,
        trigger_text=trigger_text,
        risk_text=risk_text,
        citations=unique,
    )
    return {
        "gameVersionId": str(context.game_version_id),
        "content": compose_narrative(sections),
        "sections": sections,
        "citations": [citation.to_dict() for citation in unique],
    }


def _closest_to_target(comparison, citations: list) -> str:
    targets: list[tuple[uuid.UUID, float, float]] = []
    for entry in comparison.simulations:
        validation = entry.results.rtp_validation
        if validation is None:
            continue
        distance = abs(validation.actual_rtp - validation.target_rtp)
        targets.append((entry.simulation_id, distance, validation.actual_rtp))

    if not targets:
        return (
            "No stored RTP validation targets were available to determine "
            "which simulation is closest to target."
        )

    best_sim, distance, actual = min(targets, key=lambda item: item[1])
    citation = cite(
        label=f"Simulation #{str(best_sim)[:8]}",
        source="simulation_results",
        path="mathematics_report.rtpValidation.actualRtp",
        value=round(actual, 4),
    )
    citations.append(citation)
    return grounded_sentence(
        (
            f"Simulation {str(best_sim)[:8]} is closest to its configured target "
            f"with actual RTP {actual:.2f}% (distance {distance:.2f} percentage points)."
        ),
        citation,
    )
