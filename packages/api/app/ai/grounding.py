"""Citation and grounding helpers for AI assistant responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GroundedCitation:
    """A single grounded reference to a stored artifact field."""

    label: str
    source: str
    path: str
    value: str | float | int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "label": self.label,
            "source": self.source,
            "path": self.path,
        }
        if self.value is not None:
            payload["value"] = self.value
        return payload

    def inline(self) -> str:
        """Return an inline citation fragment for narrative text."""
        if self.value is not None:
            return f"({self.source}.{self.path} = {self.value})"
        return f"({self.source}.{self.path})"


def cite(
    *,
    label: str,
    source: str,
    path: str,
    value: str | float | int | None = None,
) -> GroundedCitation:
    return GroundedCitation(label=label, source=source, path=path, value=value)


def format_percent_ratio(value: float, *, as_percent: bool = False) -> str:
    if as_percent:
        return f"{value:.2f}%"
    return f"{(value * 100):.2f}%"


def grounded_sentence(text: str, *citations: GroundedCitation) -> str:
    """Append inline citations to a factual sentence."""
    if not citations:
        return text
    refs = " ".join(citation.inline() for citation in citations)
    return f"{text} {refs}".strip()


def unique_citations(*groups: GroundedCitation) -> tuple[GroundedCitation, ...]:
    seen: set[tuple[str, str, str]] = set()
    ordered: list[GroundedCitation] = []
    for citation in groups:
        key = (citation.label, citation.source, citation.path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(citation)
    return tuple(ordered)
