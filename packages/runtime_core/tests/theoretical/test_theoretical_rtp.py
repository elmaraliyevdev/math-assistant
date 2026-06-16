"""Theoretical RTP calculator tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_fixture_01_theoretical_line_rtp() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    result = calculate_theoretical_rtp(game)
    assert result.outcome_count == 3125
    assert result.scatter_rtp == pytest.approx(0.0)
    assert result.line_rtp == pytest.approx(0.0512, abs=0.0001)
    assert result.total_rtp == pytest.approx(0.0512, abs=0.0001)


def test_wild_substitution_increases_rtp() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    baseline = calculate_theoretical_rtp(game).total_rtp

    payload = game.model_dump(mode="json", by_alias=True)
    payload["symbols"]["WILD"] = {
        "id": "WILD",
        "type": "wild",
        "substitutes": ["H1"],
    }
    payload["reelSets"]["base_game"]["reels"][0]["symbols"] = [
        "WILD",
        "H1",
        "L1",
        "L1",
        "L1",
    ]
    wild_game = GameVersion.model_validate(payload)
    with_wild = calculate_theoretical_rtp(wild_game).total_rtp
    assert with_wild >= baseline


def test_scatter_pays_contribute_to_scatter_rtp() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    payload["symbols"]["SCATTER"]["pays"] = True
    payload["paytable"]["pays"].append(
        {"symbolId": "SCATTER", "count": 3, "multiplier": 5},
    )
    scatter_game = GameVersion.model_validate(payload)
    result = calculate_theoretical_rtp(scatter_game)
    assert result.scatter_rtp > 0.0
    assert result.total_rtp == pytest.approx(result.line_rtp + result.scatter_rtp)
