"""Grounded calibration and tuning recommendations."""

from __future__ import annotations

from app.ai.context_builder import SimulationArtifactContext
from app.ai.grounding import cite, grounded_sentence, unique_citations
from app.ai.prompt_builder import build_recommendation_sections, compose_narrative


def recommend_calibration(
    context: SimulationArtifactContext,
    *,
    target_rtp: float | None,
) -> dict:
    results = context.results
    citations: list = []
    recommendations: list[dict[str, str]] = []

    actual_percent = results.summary.rtp * 100
    resolved_target = target_rtp
    if resolved_target is None and results.rtp_validation is not None:
        resolved_target = results.rtp_validation.target_rtp

    target_citation = None
    if resolved_target is not None:
        target_citation = cite(
            label="Calibration Report",
            source="calibration_report",
            path="calibration.targetRtp",
            value=round(resolved_target, 4),
        )
        gap = actual_percent - resolved_target
        summary = grounded_sentence(
            (
                f"Simulated RTP is {actual_percent:.2f}% against target "
                f"{resolved_target:.2f}% (gap {gap:+.2f} percentage points)."
            ),
            cite(
                label=f"Simulation #{str(context.simulation_id)[:8]}",
                source="simulation_results",
                path="mathematics_report.rtp.rtp",
                value=round(results.summary.rtp, 6),
            ),
            target_citation,
        )
        citations.append(target_citation)
    else:
        summary = grounded_sentence(
            f"Simulated RTP is {actual_percent:.2f}% with no explicit target RTP in the request.",
            cite(
                label=f"Simulation #{str(context.simulation_id)[:8]}",
                source="simulation_results",
                path="mathematics_report.rtp.rtp",
                value=round(results.summary.rtp, 6),
            ),
        )

    for item in results.recommendations:
        recommendations.append(
            {
                "severity": item.severity,
                "category": "simulation_insights",
                "action": item.description,
                "expectedRtpImpact": (
                    "Derived from stored simulation mathematics recommendations."
                ),
            },
        )
        citations.append(
            cite(
                label="Mathematics Report",
                source="simulation_results",
                path=f"mathematics_report.recommendations.{item.title}",
            ),
        )

    if context.calibration is not None:
        for rec in context.calibration.recommendations:
            recommendations.append(
                {
                    "severity": rec.severity,
                    "category": rec.category,
                    "action": rec.action,
                    "expectedRtpImpact": rec.expected_rtp_impact,
                    "estimatedRtpContributionPp": rec.estimated_rtp_contribution_pp,
                    "priority": rec.priority,
                    "discrepancySeverity": rec.discrepancy_severity,
                },
            )
            citations.append(
                cite(
                    label="Calibration Report",
                    source="calibration_report",
                    path=f"recommendations.{rec.category}",
                ),
            )

    if not recommendations:
        recommendations.append(
            {
                "severity": "info",
                "category": "status",
                "action": (
                    "No stored tuning recommendations are available. "
                    "Run calibration with a target RTP to generate grounded suggestions."
                ),
                "expectedRtpImpact": "N/A",
            },
        )

    unique = unique_citations(*citations)
    sections = build_recommendation_sections(
        summary=summary,
        recommendations=recommendations,
        citations=unique,
    )
    return {
        "simulationId": str(context.simulation_id),
        "targetRtp": resolved_target,
        "content": compose_narrative(sections),
        "sections": sections,
        "recommendations": recommendations,
        "citations": [citation.to_dict() for citation in unique],
    }
