"""Prompt section builders for grounded assistant responses."""

from __future__ import annotations

from typing import Any

from app.ai.grounding import GroundedCitation, grounded_sentence, unique_citations


def build_analysis_sections(
  *,
  rtp_text: str,
  feature_text: str,
  volatility_text: str,
  exposure_text: str,
  citations: tuple[GroundedCitation, ...],
) -> list[dict[str, Any]]:
    return [
        {"title": "RTP Decomposition", "content": rtp_text},
        {"title": "Feature Contribution", "content": feature_text},
        {"title": "Volatility", "content": volatility_text},
        {"title": "Exposure", "content": exposure_text},
        {"title": "Citations", "content": _citation_summary(citations)},
    ]


def build_recommendation_sections(
    *,
    summary: str,
    recommendations: list[dict[str, str]],
    citations: tuple[GroundedCitation, ...],
) -> list[dict[str, Any]]:
    items = [
        {"title": "Summary", "content": summary},
    ]
    for index, recommendation in enumerate(recommendations, start=1):
        items.append(
            {
                "title": f"Recommendation {index}",
                "content": (
                    f"{recommendation['action']} "
                    f"Expected impact: {recommendation['expectedRtpImpact']}"
                ),
            },
        )
    items.append({"title": "Citations", "content": _citation_summary(citations)})
    return items


def build_comparison_sections(
    *,
    rtp_diff_text: str,
    feature_diff_text: str,
    target_text: str,
    tradeoff_text: str,
    citations: tuple[GroundedCitation, ...],
) -> list[dict[str, Any]]:
    return [
        {"title": "RTP Differences", "content": rtp_diff_text},
        {"title": "Feature Changes", "content": feature_diff_text},
        {"title": "Target Proximity", "content": target_text},
        {"title": "Volatility vs RTP Trade-offs", "content": tradeoff_text},
        {"title": "Citations", "content": _citation_summary(citations)},
    ]


def build_game_design_sections(
    *,
    structure_text: str,
    rtp_text: str,
    trigger_text: str,
    risk_text: str,
    citations: tuple[GroundedCitation, ...],
) -> list[dict[str, Any]]:
    return [
        {"title": "Feature Structure", "content": structure_text},
        {"title": "RTP Targets", "content": rtp_text},
        {"title": "Trigger Probabilities", "content": trigger_text},
        {"title": "Risk Profile", "content": risk_text},
        {"title": "Citations", "content": _citation_summary(citations)},
    ]


def compose_narrative(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in sections:
        if section["title"] == "Citations":
            continue
        parts.append(f"## {section['title']}\n{section['content']}")
    return "\n\n".join(parts)


def _citation_summary(citations: tuple[GroundedCitation, ...]) -> str:
    if not citations:
        return "No grounded citations available."
    lines = [f"- {citation.label}: {citation.source}.{citation.path}" for citation in citations]
    return "\n".join(lines)


def merge_citations(*groups: tuple[GroundedCitation, ...]) -> tuple[GroundedCitation, ...]:
    merged: list[GroundedCitation] = []
    for group in groups:
        merged.extend(group)
    return unique_citations(*merged)
