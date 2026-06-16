"""Grounding helper tests."""

from __future__ import annotations

from app.ai.grounding import cite, format_percent_ratio, grounded_sentence, unique_citations


def test_grounded_sentence_includes_citation() -> None:
    citation = cite(
        label="Mathematics Report",
        source="simulation_results",
        path="mathematics_report.rtp.rtp",
        value=0.96,
    )
    text = grounded_sentence("RTP is 96%.", citation)
    assert "simulation_results.mathematics_report.rtp.rtp" in text
    assert "0.96" in text


def test_unique_citations_deduplicates() -> None:
    first = cite(label="A", source="simulation_results", path="rtp")
    second = cite(label="A", source="simulation_results", path="rtp")
    third = cite(label="B", source="comparison_report", path="rtp")
    result = unique_citations(first, second, third)
    assert len(result) == 2


def test_format_percent_ratio() -> None:
    assert format_percent_ratio(0.512) == "51.20%"
    assert format_percent_ratio(96.0, as_percent=True) == "96.00%"
