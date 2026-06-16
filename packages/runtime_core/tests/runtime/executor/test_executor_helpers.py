"""Unit tests for SessionExecutor helper modules."""

from __future__ import annotations

from runtime_core.runtime.executor.inheritance import inherit_spawn_context
from runtime_core.runtime.executor.multiplier import resolve_multiplier_config
from runtime_core.runtime.executor.termination import should_terminate_chain
from runtime_core.runtime.executor.wins import apply_step_wins
from runtime_core.runtime.frames import FrameContext
from runtime_core.runtime.session.factory import NewSessionParams, new_session_context
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.version import ENGINE_VERSION
from tests.runtime.conftest import base_game, session_test_game


def test_inherit_spawn_context_copies_entry_keys() -> None:
    parent = FrameContext(frame_local_state={"entryHeldSymbols": [], "scatterCounts": {"S": 3}})
    child = FrameContext(frame_local_state={})
    inherit_spawn_context(parent, child)
    assert child.frame_local_state["scatterCounts"] == {"S": 3}


def test_should_terminate_chain_stay(base_game) -> None:
    stack = ExecutionStack(max_depth=4)
    stack.push_root(base_game)
    assert should_terminate_chain(effect="stay", stack=stack, game=base_game)


def test_should_terminate_chain_pop_to_root(base_game) -> None:
    stack = ExecutionStack(max_depth=4)
    stack.push_root(base_game)
    assert should_terminate_chain(effect="pop", stack=stack, game=base_game)


def test_should_not_terminate_goto_free_spins(base_game) -> None:
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    from runtime_core.domain.state_machine import State
    from runtime_core.runtime.stack.frame import build_frame

    fs_state = base_game.state_machines["main"].states.get("FREE_SPINS")
    if fs_state is None:
        return
    updated = build_frame(
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state=fs_state,
        frame_context=frame.frame_context,
        frozen=False,
    )
    stack.replace_top(updated)
    assert not should_terminate_chain(effect="goto", stack=stack, game=base_game)


def test_apply_step_wins_enforces_exposure_cap() -> None:
    game = session_test_game()
    params = NewSessionParams(
        game=game,
        engine_version=ENGINE_VERSION,
        master_seed=b"cap-test",
        spin_chain_index=0,
        shard_index=0,
        simulation_run_id="cap",
    )
    session = new_session_context(params)
    session.exposure = type(session.exposure)(
        enforce_cap=True,
        effective_cap_minor=50,
        cap_scope="session_spin_chain",
        max_win_minor_units=50,
        max_win_multiplier=0,
    )
    result = apply_step_wins(
        session,
        [{"source": "lines", "symbolId": "H1", "count": 3, "winMinorUnits": 100}],
    )
    assert result.capped_total == 50
    assert result.truncated == 50
    assert session.total_win_minor_units == 50


def test_apply_step_wins_without_enforcement() -> None:
    game = session_test_game()
    params = NewSessionParams(
        game=game,
        engine_version=ENGINE_VERSION,
        master_seed=b"no-cap",
        spin_chain_index=0,
        shard_index=0,
        simulation_run_id="cap",
    )
    session = new_session_context(params)
    session.exposure = type(session.exposure)(
        enforce_cap=False,
        effective_cap_minor=0,
        cap_scope="session_spin_chain",
        max_win_minor_units=0,
        max_win_multiplier=0,
    )
    wins = [{"source": "lines", "symbolId": "H1", "count": 3, "winMinorUnits": 25}]
    result = apply_step_wins(session, wins)
    assert result.capped_total == 25
    assert session.total_win_minor_units == 25


def test_apply_step_wins_empty_and_zero() -> None:
    game = session_test_game()
    params = NewSessionParams(
        game=game,
        engine_version=ENGINE_VERSION,
        master_seed=b"zero",
        spin_chain_index=0,
        shard_index=0,
        simulation_run_id="z",
    )
    session = new_session_context(params)
    assert apply_step_wins(session, []).capped_total == 0
    assert apply_step_wins(
        session,
        [{"source": "lines", "symbolId": "H1", "count": 3, "winMinorUnits": 0}],
    ).capped_total == 0


def test_apply_step_wins_cap_already_reached() -> None:
    game = session_test_game()
    params = NewSessionParams(
        game=game,
        engine_version=ENGINE_VERSION,
        master_seed=b"full-cap",
        spin_chain_index=0,
        shard_index=0,
        simulation_run_id="full",
    )
    session = new_session_context(params)
    session.exposure = type(session.exposure)(
        enforce_cap=True,
        effective_cap_minor=10,
        cap_scope="session_spin_chain",
        max_win_minor_units=10,
        max_win_multiplier=0,
    )
    session.total_win_minor_units = 10
    result = apply_step_wins(
        session,
        [{"source": "lines", "symbolId": "H1", "count": 3, "winMinorUnits": 5}],
    )
    assert result.capped_total == 0
    assert result.truncated == 5


def test_should_terminate_goto_base(base_game) -> None:
    stack = ExecutionStack(max_depth=4)
    stack.push_root(base_game)
    assert should_terminate_chain(effect="goto", stack=stack, game=base_game)


def test_should_terminate_empty_stack(base_game) -> None:
    stack = ExecutionStack(max_depth=4)
    assert should_terminate_chain(effect="goto", stack=stack, game=base_game)


def test_apply_frame_multiplier_fixed() -> None:
    from runtime_core.runtime.executor.multiplier import apply_frame_multiplier
    from runtime_core.runtime.rng import RNGService

    game = session_test_game()
    payload = game.to_json_dict()
    payload["extensions"] = {
        "multiplierConfigs": {
            "mult": {
                "mode": "fixed",
                "value": 3,
                "scope": "frame",
                "applyTo": "all_wins_in_frame",
            },
        },
    }
    from runtime_core.domain.game_version import GameVersion

    game = GameVersion.model_validate(payload)
    params = NewSessionParams(
        game=game,
        engine_version=ENGINE_VERSION,
        master_seed=b"mult",
        spin_chain_index=0,
        shard_index=0,
        simulation_run_id="m",
    )
    session = new_session_context(params)
    stream = session.chain_rng.frame_stream("f-0-0")
    wins = [{"source": "lines", "symbolId": "H1", "count": 3, "winMinorUnits": 10}]
    adjusted, factor = apply_frame_multiplier(
        game,
        session,
        multiplier_ref_id="mult",
        wins=wins,
        frame_stream=stream,
        apply_index=0,
    )
    assert factor == 3
    assert adjusted[0]["winMinorUnits"] == 30


def test_resolve_multiplier_config_from_extensions(base_game) -> None:
    payload = base_game.to_json_dict()
    payload["extensions"] = {
        "multiplierConfigs": {"mult_test": {"mode": "fixed", "value": 2}},
    }
    from runtime_core.domain.game_version import GameVersion

    game = GameVersion.model_validate(payload)
    config = resolve_multiplier_config(game, "mult_test")
    assert config == {"mode": "fixed", "value": 2}
