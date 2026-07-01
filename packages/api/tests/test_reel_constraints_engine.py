from __future__ import annotations

from app.reel_constraints.engine import ConstraintDocument, ConstraintRule, run_constraint_engine

SYMBOLS = {
    "S": {"id": "S", "type": "scatter"},
    "W": {"id": "W", "type": "wild"},
    "A": {"id": "A", "type": "regular"},
}

REEL_SET = {
    "id": "base_game",
    "reels": [
        {"reelIndex": 0, "symbols": ["S", "A", "A", "B", "S"]},
        {"reelIndex": 1, "symbols": ["W", "W", "A", "B", "A"]},
    ],
}


def test_min_count_passes() -> None:
    document = ConstraintDocument(
        constraints=[
            ConstraintRule(
                id="min-s",
                type="min_count",
                targetType="symbol",
                targetId="S",
                value=2,
            )
        ]
    )
    report = run_constraint_engine(REEL_SET, SYMBOLS, document)
    assert report.results[0].status == "pass"


def test_forbidden_adjacency_with_wrap() -> None:
    reel_set = {"id": "base", "reels": [{"reelIndex": 0, "symbols": ["S", "A", "B", "A", "S"]}]}
    document = ConstraintDocument(
        edgeWrapping=True,
        constraints=[
            ConstraintRule(
                id="no-touch",
                type="forbidden_adjacency",
                targetType="symbol",
                targetId="S",
            )
        ],
    )
    report = run_constraint_engine(reel_set, SYMBOLS, document)
    assert report.results[0].status == "error"
