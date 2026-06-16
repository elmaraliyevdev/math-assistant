"""Infinite progression loop detection."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.state_machine import StateMachine
from runtime_core.validation.validators.finding import Finding, err_finding


def validate_progression(game: GameVersion | None) -> list[Finding]:
    findings: list[Finding] = []
    if game is None:
        return findings
    for machine_id, machine in game.state_machines.items():
        for state_id, state in machine.states.items():
            if state.terminal or state.state_type != "multi_step":
                continue
            if state.progression is not None and state.progression.terminates_when:
                continue
            if _has_self_stay_loop(machine, state_id):
                findings.append(
                    err_finding(
                        "GV-011",
                        f"stateMachines.{machine_id}.states.{state_id}",
                        (
                            "infinite progression loop detected without "
                            "terminating progression metadata"
                        ),
                        "Add progression metadata or a terminating transition",
                    ),
                )
    return findings


def _has_self_stay_loop(machine: StateMachine, state_id: str) -> bool:
    state = machine.states.get(state_id)
    if state is None:
        return False
    for transition in state.transitions:
        if transition.effect != "stay" or transition.target_state_id != state_id:
            continue
        has_exit = any(
            other.effect != "stay" or other.target_state_id != state_id
            for other in state.transitions
        )
        if not has_exit:
            return True
    return False
