"""Hypothesis property tests for graph invariants."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st
from tests.validation.conftest import build_nested_fs_haw, build_valid_base_game

from runtime_core.validation.validators.reachability_validator import (
    _compute_reachable_states,
)
from runtime_core.validation.validators.stack_depth_validator import (
    worst_case_stack_depth,
)


@given(st.integers(min_value=1, max_value=16))
def test_worst_case_stack_depth_is_at_least_one(extra_depth: int) -> None:
    game = build_nested_fs_haw()
    game.session.max_stack_depth = extra_depth
    depth = worst_case_stack_depth(game, game.session.root_machine_id, {})
    assert depth >= 1


def test_reachable_states_subset_of_all_states() -> None:
    game = build_nested_fs_haw()
    reachable = _compute_reachable_states(game)
    all_states = {
        f"{machine_id}.{state_id}"
        for machine_id, machine in game.state_machines.items()
        for state_id in machine.states
    }
    assert reachable.issubset(all_states)
    assert (
        f"{game.session.root_machine_id}.{game.state_machines['main'].initial_state_id}"
        in reachable
    )


@given(st.sampled_from(["fixture-01-base-5x3", "fixture-04-nested-fs-hold-win"]))
def test_golden_games_have_consistent_stack_and_reachability(fixture_id: str) -> None:
    from runtime_core.common.golden import load_golden_game_version

    game = load_golden_game_version(fixture_id)
    reachable = _compute_reachable_states(game)
    assert reachable
    depth = worst_case_stack_depth(game, game.session.root_machine_id, {})
    assert depth <= max(game.session.max_stack_depth, 1)


def test_increasing_spawn_depth_never_reduces_worst_case() -> None:
    shallow = build_valid_base_game()
    nested = build_nested_fs_haw()
    shallow_depth = worst_case_stack_depth(shallow, shallow.session.root_machine_id, {})
    nested_depth = worst_case_stack_depth(nested, nested.session.root_machine_id, {})
    assert nested_depth >= shallow_depth


def test_unreachable_state_not_in_reachable_set() -> None:
    game = build_valid_base_game()
    reachable_before = _compute_reachable_states(game)
    game.state_machines["main"].states["ORPHAN"] = (
        game.state_machines["main"].states["BASE"].model_copy(update={"id": "ORPHAN"})
    )
    reachable_after = _compute_reachable_states(game)
    assert "main.ORPHAN" not in reachable_after
    assert reachable_after.issubset(reachable_before | {"main.ORPHAN"})
