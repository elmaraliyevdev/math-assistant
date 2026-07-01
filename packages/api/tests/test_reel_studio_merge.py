from __future__ import annotations

from app.reel_studio.merge import merge_reel_sets_into_canonical, serialize_reel_sets

FIXTURE = {
    "schemaVersion": "1.0.0",
    "metadata": {"title": "Test"},
    "symbols": {"A": {"id": "A", "type": "regular"}},
    "reelSets": {
        "base_game": {
            "id": "base_game",
            "reels": [{"reelIndex": 0, "symbols": ["A", "A"]}],
        }
    },
}


def test_merge_preserves_non_reel_fields_and_order() -> None:
    edited_reel_sets = {
        "base_game": {
            "id": "base_game",
            "reels": [{"reelIndex": 0, "symbols": ["A", "A", "A"]}],
        }
    }
    merged = merge_reel_sets_into_canonical(FIXTURE, edited_reel_sets)
    assert list(merged.keys()) == list(FIXTURE.keys())
    assert merged["metadata"] == FIXTURE["metadata"]
    assert merged["symbols"] == FIXTURE["symbols"]
    reels = merged["reelSets"]["base_game"]["reels"]
    assert reels[0]["symbols"] == ["A", "A", "A"]


def test_serialize_reel_sets() -> None:
    serialized = serialize_reel_sets(FIXTURE["reelSets"])
    assert serialized["base_game"]["id"] == "base_game"
