"""Clustering and spacing analysis."""

from __future__ import annotations

import math

from runtime_core.intelligence.models import IntelligenceSnapshot


def clustering_score(snapshot: IntelligenceSnapshot, symbol_id: str) -> float:
    positions: list[tuple[int, int]] = []
    position_counts = snapshot.symbol_position_counts.get(symbol_id, {})
    for key, count in position_counts.items():
        reel_str, pos_str = key.split(":", 1)
        for _ in range(count):
            positions.append((int(reel_str), int(pos_str)))
    if len(positions) < 2:
        return 0.0
    positions.sort()
    gaps = [
        positions[index + 1][1] - positions[index][1]
        for index in range(len(positions) - 1)
        if positions[index][0] == positions[index + 1][0]
    ]
    if not gaps:
        return 0.0
    avg_gap = sum(gaps) / len(gaps)
    return max(0.0, min(1.0, 1.0 / max(avg_gap, 1.0)))


def average_spacing(snapshot: IntelligenceSnapshot, symbol_id: str) -> float | None:
    position_counts = snapshot.symbol_position_counts.get(symbol_id, {})
    if not position_counts:
        return None
    weighted = 0.0
    total = 0
    for key, count in position_counts.items():
        _, pos_str = key.split(":", 1)
        weighted += int(pos_str) * count
        total += count
    if total == 0:
        return None
    return weighted / total


def reel_entropy(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count <= 0:
            continue
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy
