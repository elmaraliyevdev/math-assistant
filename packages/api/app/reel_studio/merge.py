"""Reel Studio helper utilities (editor-only; no runtime simulation changes)."""

from __future__ import annotations

from typing import Any


def _serialize_reel_set(reel_set: dict[str, Any]) -> dict[str, Any]:
    reels_out: list[dict[str, Any]] = []
    for reel in reel_set.get("reels", []):
        if not isinstance(reel, dict):
            continue
        payload: dict[str, Any] = {
            "reelIndex": reel.get("reelIndex"),
            "symbols": list(reel.get("symbols", [])),
        }
        weights = reel.get("weights")
        if isinstance(weights, list) and weights:
            payload["weights"] = list(weights)
        reels_out.append(payload)
    return {
        "id": reel_set.get("id"),
        "reels": reels_out,
    }


def serialize_reel_sets(reel_sets: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in reel_sets.items():
        if isinstance(value, dict):
            serialized[key] = _serialize_reel_set(value)
    return serialized


def merge_reel_sets_into_canonical(
    canonical_json: dict[str, Any],
    reel_sets: dict[str, Any],
) -> dict[str, Any]:
    serialized = serialize_reel_sets(reel_sets)
    merged: dict[str, Any] = {}
    wrote_reel_sets = False
    for key, value in canonical_json.items():
        if key == "reelSets":
            merged[key] = serialized
            wrote_reel_sets = True
        else:
            merged[key] = value
    if not wrote_reel_sets:
        merged["reelSets"] = serialized
    return merged
