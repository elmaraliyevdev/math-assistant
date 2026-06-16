"""Prompt builder tests."""

from __future__ import annotations

from app.ai.grounding import cite
from app.ai.prompt_builder import (
    build_analysis_sections,
    compose_narrative,
    merge_citations,
)


def test_compose_narrative_skips_citation_section() -> None:
    sections = build_analysis_sections(
        rtp_text="RTP text",
        feature_text="Feature text",
        volatility_text="Volatility text",
        exposure_text="Exposure text",
        citations=(
            cite(label="Mathematics Report", source="simulation_results", path="rtp"),
        ),
    )
    narrative = compose_narrative(sections)
    assert "RTP text" in narrative
    assert "Citations" not in narrative


def test_merge_citations() -> None:
    first = (cite(label="A", source="simulation_results", path="rtp"),)
    second = (cite(label="B", source="comparison_report", path="rtp"),)
    merged = merge_citations(first, second)
    assert len(merged) == 2
