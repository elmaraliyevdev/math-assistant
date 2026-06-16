"""Natural-language explanations grounded in stored simulation artifacts."""

from __future__ import annotations

from app.ai.context_builder import SimulationArtifactContext, decomposition_chart_dict
from app.ai.grounding import cite, format_percent_ratio, grounded_sentence, unique_citations
from app.ai.prompt_builder import build_analysis_sections, compose_narrative, merge_citations


def explain_simulation(context: SimulationArtifactContext) -> dict:
    results = context.results
    chart = decomposition_chart_dict(results)
    citations: list = []

    rtp_citation = cite(
        label="Mathematics Report",
        source="simulation_results",
        path="mathematics_report.rtpDecompositionChart.totalRtp",
        value=round(chart["totalRtp"], 4),
    )
    rtp_text = grounded_sentence(
        (
            f"Total simulated RTP is {format_percent_ratio(results.summary.rtp)} "
            f"with decomposition BASE {chart['BASE']:.2f}%, "
            f"FREE_SPINS {chart['FREE_SPINS']:.2f}%, "
            f"HOLD_AND_WIN {chart['HOLD_AND_WIN']:.2f}%, "
            f"and JACKPOT {chart['JACKPOT']:.2f}%."
        ),
        rtp_citation,
        cite(
            label="Mathematics Report",
            source="simulation_results",
            path="mathematics_report.rtpDecompositionChart.BASE",
            value=round(chart["BASE"], 4),
        ),
        cite(
            label="Mathematics Report",
            source="simulation_results",
            path="mathematics_report.rtpDecompositionChart.FREE_SPINS",
            value=round(chart["FREE_SPINS"], 4),
        ),
    )
    citations.extend([rtp_citation])

    feature_lines: list[str] = []
    for feature in results.feature_frequencies:
        freq_pct = feature.frequency * 100
        feature_citation = cite(
            label=f"Simulation #{str(context.simulation_id)[:8]}",
            source="simulation_results",
            path=f"mathematics_report.featureFrequencies.{feature.feature_name}",
            value=round(feature.frequency, 6),
        )
        one_in = f", about 1 in {feature.one_in_x:.2f}" if feature.one_in_x else ""
        feature_lines.append(
            grounded_sentence(
                f"{feature.feature_name} triggered on {freq_pct:.4f}% of spins{one_in}.",
                feature_citation,
            ),
        )
        citations.append(feature_citation)
    if not feature_lines:
        feature_lines.append(
            "No feature trigger frequencies were recorded in the stored mathematics report.",
        )
    feature_text = " ".join(feature_lines)

    vol_citation = cite(
        label="Mathematics Report",
        source="simulation_results",
        path="mathematics_report.volatility.standardDeviation",
        value=round(results.summary.volatility, 4),
    )
    volatility_text = grounded_sentence(
        (
            f"Volatility (standard deviation of win per spin) is "
            f"{results.summary.volatility:.4f} minor units "
            f"with hit frequency {results.summary.hit_frequency * 100:.2f}%."
        ),
        vol_citation,
        cite(
            label="Mathematics Report",
            source="simulation_results",
            path="mathematics_report.hitFrequency.hitFrequency",
            value=round(results.summary.hit_frequency, 6),
        ),
    )
    citations.append(vol_citation)

    exposure = results.exposure
    exposure_citation = cite(
        label="Mathematics Report",
        source="simulation_results",
        path="mathematics_report.exposure.truncationRate",
        value=round(exposure.truncation_rate, 6),
    )
    exposure_text = grounded_sentence(
        (
            f"Exposure truncation rate is {exposure.truncation_rate * 100:.4f}% "
            f"with capped RTP {format_percent_ratio(exposure.capped_rtp)} "
            f"vs uncapped {format_percent_ratio(exposure.uncapped_rtp)} "
            f"(difference {format_percent_ratio(exposure.rtp_difference)})."
        ),
        exposure_citation,
        cite(
            label="Mathematics Report",
            source="simulation_results",
            path="mathematics_report.exposure.rtpDifference",
            value=round(exposure.rtp_difference, 6),
        ),
    )
    citations.append(exposure_citation)

    if context.theoretical is not None:
        theory_pct = context.theoretical.rtp.total_rtp * 100
        citations.append(
            cite(
                label="Theoretical Analysis",
                source="theoretical_analysis",
                path="rtp.totalRtp",
                value=round(theory_pct, 4),
            ),
        )

    unique = unique_citations(*citations)
    sections = build_analysis_sections(
        rtp_text=rtp_text,
        feature_text=feature_text,
        volatility_text=volatility_text,
        exposure_text=exposure_text,
        citations=unique,
    )
    return {
        "simulationId": str(context.simulation_id),
        "content": compose_narrative(sections),
        "sections": sections,
        "citations": [citation.to_dict() for citation in unique],
    }
