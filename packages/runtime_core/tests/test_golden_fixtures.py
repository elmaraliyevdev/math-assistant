"""Golden fixture loading tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from runtime_core.common.golden import list_golden_fixtures
from runtime_core.domain.game_version import GameVersion


@pytest.mark.golden
def test_list_golden_fixtures_includes_mvp_fixtures() -> None:
    fixtures = list_golden_fixtures()
    assert "fixture-01-base-5x3" in fixtures
    assert "fixture-02-base-free-spins" in fixtures
    assert "fixture-03-base-hold-win" in fixtures
    assert "fixture-04-nested-fs-hold-win" in fixtures


@pytest.mark.golden
@pytest.mark.parametrize(
    "fixture_id",
    [
        "fixture-01-base-5x3",
        "fixture-02-base-free-spins",
        "fixture-03-base-hold-win",
        "fixture-04-nested-fs-hold-win",
    ],
)
def test_load_golden_game_version(
    load_golden: Callable[[str], GameVersion],
    fixture_id: str,
) -> None:
    game = load_golden(fixture_id)
    assert game.schema_version == "1.0.0"
    assert game.determinism.rng_algorithm == "PCG64"
    assert game.session.root_machine_id == "main"
