"""Runtime limits consistency validation."""

from __future__ import annotations

from typing import Any

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.issues import (
    graph_limits_frames_exceed_stack,
    graph_limits_respins_exceeded,
)
from runtime_core.validation.report import ValidationReport


class LimitsValidator:
    def validate(self, game: GameVersion | None) -> ValidationReport:
        report = ValidationReport.empty()
        if game is None:
            return report
        limits = game.session.runtime_limits
        if limits is None:
            return report
        stack = game.session.max_stack_depth or 8
        max_frames = limits.max_frames_per_chain or 0
        if max_frames > 0 and max_frames > stack:
            report.add_error(graph_limits_frames_exceed_stack(max_frames, stack))
        max_respins = limits.max_respins_per_feature or 0
        if max_respins <= 0:
            return report
        for machine_id, machine in game.state_machines.items():
            for state_id, state in machine.states.items():
                respins = _read_initial_respins(state.plugin_config)
                if respins is None:
                    continue
                if respins > max_respins:
                    path = (
                        f"stateMachines.{machine_id}.states.{state_id}"
                        ".pluginConfig.initialRespins"
                    )
                    report.add_error(
                        graph_limits_respins_exceeded(path, respins, max_respins)
                    )
        return report


def _read_initial_respins(config: dict[str, Any]) -> int | None:
    if not config:
        return None
    value = config.get("initialRespins")
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None
