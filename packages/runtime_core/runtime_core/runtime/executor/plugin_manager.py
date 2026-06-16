"""Plugin binding lifecycle for SessionExecutor."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.bindings import PluginGameBindings, plugin_game_bindings
from runtime_core.runtime.plugins.host import PluginHandle, PluginHost
from runtime_core.runtime.stack.frame import StateMachineFrame


class PluginManager:
    """Tracks active plugin handles per frame across spawn/pop/goto."""

    def __init__(
        self,
        host: PluginHost,
        game: GameVersion,
        *,
        total_bet_minor_units: int,
    ) -> None:
        self._host = host
        self._game = game
        self._bindings = plugin_game_bindings(
            game,
            total_bet_minor_units=total_bet_minor_units,
        )
        self._handles: dict[str, PluginHandle] = {}

    @property
    def bindings(self) -> PluginGameBindings:
        return self._bindings

    def ensure_bound(self, frame: StateMachineFrame) -> PluginHandle:
        existing = self._handles.get(frame.frame_id)
        if existing is not None and existing.context.state_id == frame.state_id:
            return existing
        if existing is not None:
            self.release_frame(frame.frame_id)
        state = self._game.state_machines[frame.machine_id].states[frame.state_id]
        plugin_ref = self._game.plugins[state.plugin_ref_id]
        handle = self._host.bind(
            plugin_ref,
            frame,
            plugin_config=dict(state.plugin_config or {}),
            game_bindings=self._bindings,
        )
        self._host.apply_enter_result(handle)
        self._handles[frame.frame_id] = handle
        return handle

    def release_frame(self, frame_id: str) -> None:
        handle = self._handles.pop(frame_id, None)
        if handle is not None:
            self._host.release(handle)

    def release_all(self) -> None:
        for frame_id in list(self._handles):
            self.release_frame(frame_id)
