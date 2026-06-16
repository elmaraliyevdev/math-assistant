"""Transition resolution tests."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


def test_base_only_spin_complete_stay(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    result = resolve_transition(base_game, frame, ["SPIN_COMPLETE"], priority_tiers)
    assert result.fault is None
    assert result.resolution is not None
    assert result.resolution.selected_token == "SPIN_COMPLETE"
    assert result.resolution.transition.id == "t_spin"
    assert result.resolution.transition.effect == "stay"


def test_empty_tokens_fallback_to_spin_complete(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    result = resolve_transition(
        base_game,
        frame,
        [],
        priority_tiers,
        step_complete=True,
    )
    assert result.resolution is not None
    assert result.resolution.selected_token == "SPIN_COMPLETE"


def test_empty_tokens_multistep_when_not_complete(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    result = resolve_transition(
        nested_game,
        frame,
        [],
        priority_tiers,
        step_complete=False,
    )
    assert result.continue_multistep is True
    assert result.resolution is None
    assert result.fault is None


def test_base_to_free_spins_goto(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    result = resolve_transition(nested_game, frame, ["FREE_SPINS"], priority_tiers)
    assert result.resolution is not None
    assert result.resolution.transition.id == "t_base_to_fs"
    assert result.resolution.transition.effect == "goto"
    assert result.resolution.transition.target_state_id == "FREE_SPINS"


def test_phase_a_hold_and_win_beats_free_spins(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    result = resolve_transition(
        nested_game,
        frame,
        ["FREE_SPINS", "HOLD_AND_WIN"],
        priority_tiers,
    )
    assert result.resolution is not None
    assert result.resolution.selected_token == "HOLD_AND_WIN"
    assert result.resolution.transition.effect == "spawn"


def test_free_spins_to_hold_and_win_spawn(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    root = stack.push_root(nested_game)
    fs = nested_game.state_machines["main"].states["FREE_SPINS"]
    from runtime_core.runtime.stack import build_frame

    fs_frame = build_frame(
        frame_id=root.frame_id,
        machine_id=root.machine_id,
        state=fs,
    )
    stack.replace_top(fs_frame)
    result = resolve_transition(
        nested_game,
        fs_frame,
        ["HOLD_AND_WIN"],
        priority_tiers,
    )
    assert result.resolution is not None
    assert result.resolution.transition.id == "t_fs_to_haw"
    assert result.resolution.transition.effect == "spawn"


def test_feature_complete_pop_from_haw(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    stack.push_root(nested_game)
    haw_frame = stack.push_child(nested_game, "hold_and_win")
    result = resolve_transition(
        nested_game,
        haw_frame,
        ["FEATURE_COMPLETE"],
        priority_tiers,
    )
    assert result.resolution is not None
    assert result.resolution.transition.id == "t_haw_pop"
    assert result.resolution.transition.effect == "pop"


def test_ambiguous_trigger_unknown_in_multi_token_set(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    result = resolve_transition(
        nested_game,
        frame,
        ["FREE_SPINS", "UNKNOWN"],
        priority_tiers,
    )
    assert result.fault is not None
    assert result.fault.code == "AMBIGUOUS_TRIGGER"


def test_token_missing_from_trigger_order(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    result = resolve_transition(
        base_game,
        frame,
        ["UNKNOWN_TOKEN"],
        priority_tiers,
    )
    assert result.fault is not None
    assert result.fault.code == "NO_MATCHING_TRANSITION"


def test_no_matching_transition_for_token(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    result = resolve_transition(base_game, frame, ["FREE_SPINS"], priority_tiers)
    assert result.fault is not None
    assert result.fault.code == "NO_MATCHING_TRANSITION"


def test_phase_b_priority_sorting(
    nested_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(nested_game)
    result = resolve_transition(
        nested_game,
        frame,
        ["SPIN_COMPLETE"],
        priority_tiers,
    )
    assert result.resolution is not None
    assert result.resolution.transition.priority == 1000


def test_ambiguous_trigger_tie_on_index() -> None:
    from types import SimpleNamespace

    from runtime_core.runtime.transitions.resolver import _select_token

    class _Order:
        def index(self, _token: str) -> int:
            return 0

    game = SimpleNamespace(precedence=SimpleNamespace(trigger_order=_Order()))
    token, fault = _select_token(game, ["A", "B"], step_complete=True)  # type: ignore[arg-type]
    assert token is None
    assert fault is not None
    assert fault.code == "AMBIGUOUS_TRIGGER"


def test_resolve_unknown_machine(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    bad_frame = frame.__class__(
        frame_id=frame.frame_id,
        machine_id="missing",
        state_id=frame.state_id,
        plugin_ref_id=frame.plugin_ref_id,
        rtp_category=frame.rtp_category,
        frame_context=frame.frame_context,
    )
    result = resolve_transition(base_game, bad_frame, ["SPIN_COMPLETE"], priority_tiers)
    assert result.fault is not None
    assert result.fault.code == "NO_MATCHING_TRANSITION"


def test_resolve_unknown_state(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    bad_frame = frame.__class__(
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state_id="MISSING",
        plugin_ref_id=frame.plugin_ref_id,
        rtp_category=frame.rtp_category,
        frame_context=frame.frame_context,
    )
    result = resolve_transition(base_game, bad_frame, ["SPIN_COMPLETE"], priority_tiers)
    assert result.fault is not None
    assert result.fault.code == "NO_MATCHING_TRANSITION"


def test_phase_b_lexicographic_tiebreak(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    machine = base_game.state_machines["main"]
    state = machine.states["BASE"]
    first = state.transitions[0].model_copy(update={"id": "t_z"})
    second = state.transitions[0].model_copy(update={"id": "t_a"})
    patched_state = state.model_copy(update={"transitions": [first, second]})
    patched_machine = machine.model_copy(
        update={"states": {**machine.states, "BASE": patched_state}},
    )
    patched_game = base_game.model_copy(
        update={"state_machines": {**base_game.state_machines, "main": patched_machine}},
    )
    result = resolve_transition(
        patched_game,
        frame,
        ["SPIN_COMPLETE"],
        priority_tiers,
    )
    assert result.resolution is not None
    assert result.resolution.transition.id == "t_a"


def test_ambiguous_transition_equal_rank(
    base_game: GameVersion,
    priority_tiers: PriorityTierRegistry,
) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    machine = base_game.state_machines["main"]
    state = machine.states["BASE"]
    dup_a = state.transitions[0].model_copy(update={"id": "t_same"})
    dup_b = state.transitions[0].model_copy(update={"id": "t_same"})
    patched_state = state.model_copy(update={"transitions": [dup_a, dup_b]})
    patched_machine = machine.model_copy(
        update={"states": {**machine.states, "BASE": patched_state}},
    )
    patched_game = base_game.model_copy(
        update={"state_machines": {**base_game.state_machines, "main": patched_machine}},
    )
    result = resolve_transition(
        patched_game,
        frame,
        ["SPIN_COMPLETE"],
        priority_tiers,
    )
    assert result.fault is not None
    assert result.fault.code == "AMBIGUOUS_TRANSITION"
