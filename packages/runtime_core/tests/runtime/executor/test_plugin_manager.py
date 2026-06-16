"""PluginManager lifecycle tests."""

from __future__ import annotations

from runtime_core.common.golden import load_golden_game_version
from runtime_core.runtime.executor.plugin_manager import PluginManager
from runtime_core.runtime.plugins.host import PluginHost
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.stack.frame import build_frame
from tests.runtime.conftest import base_game


def test_plugin_manager_rebinds_on_state_change() -> None:
    base_game = load_golden_game_version("fixture-02-base-free-spins")
    host = PluginHost()
    manager = PluginManager(host, base_game, total_bet_minor_units=2000)
    stack = ExecutionStack(max_depth=base_game.session.max_stack_depth)
    frame = stack.push_root(base_game)
    first = manager.ensure_bound(frame)
    fs_state = base_game.state_machines["main"].states.get("FREE_SPINS")
    if fs_state is None:
        manager.release_all()
        return
    updated = build_frame(
        frame_id=frame.frame_id,
        machine_id=frame.machine_id,
        state=fs_state,
        frame_context=frame.frame_context,
        frozen=False,
    )
    updated.frame_context.frame_local_state["scatterCounts"] = {"SCATTER": 3}
    stack.replace_top(updated)
    second = manager.ensure_bound(stack.top())
    assert first is not second
    manager.release_all()


def test_plugin_manager_bindings_property(base_game) -> None:
    host = PluginHost()
    manager = PluginManager(host, base_game, total_bet_minor_units=2000)
    assert manager.bindings.total_bet_minor_units == 2000


def test_plugin_manager_release_all_idempotent(base_game) -> None:
    host = PluginHost()
    manager = PluginManager(host, base_game, total_bet_minor_units=2000)
    stack = ExecutionStack(max_depth=4)
    frame = stack.push_root(base_game)
    manager.ensure_bound(frame)
    manager.release_all()
    manager.release_all()
