"""Reachability, dead-end, and spawn/pop path validation."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.state_machine import StateMachine
from runtime_core.validation.validators.finding import Finding, err_finding


def validate_reachability(game: GameVersion | None) -> list[Finding]:
    findings: list[Finding] = []
    if game is None or not game.state_machines:
        return findings
    reachable = _compute_reachable_states(game)
    for machine_id, machine in game.state_machines.items():
        for state_id, state in machine.states.items():
            if state.deprecated:
                continue
            key = f"{machine_id}.{state_id}"
            if key not in reachable:
                findings.append(
                    err_finding(
                        "GV-005",
                        f"stateMachines.{machine_id}.states.{state_id}",
                        "state is unreachable from the session entry point",
                        "Add transitions that reach this state or mark it deprecated",
                    ),
                )
            if not state.terminal and not state.transitions:
                findings.append(
                    err_finding(
                        "GV-006",
                        f"stateMachines.{machine_id}.states.{state_id}",
                        "non-terminal state has no outgoing transitions",
                        "Add transitions or mark the state terminal",
                    ),
                )
    for machine_id in game.state_machines:
        if not _is_spawn_target(game, machine_id):
            continue
        machine = game.state_machines[machine_id]
        if not _has_pop_path(machine):
            findings.append(
                err_finding(
                    "GV-008",
                    f"stateMachines.{machine_id}",
                    "spawned machine has no pop transition path to return to parent",
                    "Add a FEATURE_COMPLETE transition with effect pop",
                ),
            )
    return findings


@dataclass(frozen=True, slots=True)
class _Frame:
    machine_id: str
    state_id: str


def _compute_reachable_states(game: GameVersion) -> set[str]:
    reachable: set[str] = set()
    root_machine_id = game.session.root_machine_id
    root_machine = game.state_machines.get(root_machine_id)
    if root_machine is None:
        return reachable
    queue = [_Frame(machine_id=root_machine_id, state_id=root_machine.initial_state_id)]
    while queue:
        current = queue.pop(0)
        key = f"{current.machine_id}.{current.state_id}"
        if key in reachable:
            continue
        reachable.add(key)
        machine = game.state_machines.get(current.machine_id)
        if machine is None:
            continue
        state = machine.states.get(current.state_id)
        if state is None:
            continue
        for transition in state.transitions:
            if transition.effect in {"goto", "stay"}:
                if transition.target_state_id:
                    queue.append(
                        _Frame(
                            machine_id=current.machine_id,
                            state_id=transition.target_state_id,
                        ),
                    )
            elif transition.effect == "spawn" and transition.target_machine_id:
                child = game.state_machines.get(transition.target_machine_id)
                if child is not None:
                    queue.append(
                        _Frame(machine_id=child.id, state_id=child.initial_state_id),
                    )
    return reachable


def _is_spawn_target(game: GameVersion, machine_id: str) -> bool:
    for machine in game.state_machines.values():
        for state in machine.states.values():
            for transition in state.transitions:
                if (
                    transition.effect == "spawn"
                    and transition.target_machine_id == machine_id
                ):
                    return True
    return False


def _has_pop_path(machine: StateMachine) -> bool:
    return any(
        transition.effect == "pop"
        for state in machine.states.values()
        for transition in state.transitions
    )
