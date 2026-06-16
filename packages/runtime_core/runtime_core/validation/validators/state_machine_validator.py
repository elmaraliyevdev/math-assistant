"""State machine identity and initial state validation."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.validators.finding import Finding, err_finding


def validate_state_machines(game: GameVersion | None) -> list[Finding]:
    findings: list[Finding] = []
    if game is None:
        return findings
    seen_machines: dict[str, str] = {}
    for key, machine in game.state_machines.items():
        existing_key = seen_machines.get(machine.id)
        if existing_key is not None and existing_key != key:
            findings.append(
                err_finding(
                    "GV-015",
                    "stateMachines",
                    f"duplicate state machine id '{machine.id}'",
                    "Ensure machine map keys match unique machine ids",
                ),
            )
        seen_machines[machine.id] = key
        if machine.id != key:
            findings.append(
                err_finding(
                    "GV-015",
                    "stateMachines",
                    f"duplicate state machine id '{key}'",
                    "Ensure machine map keys match unique machine ids",
                ),
            )
        if not machine.initial_state_id:
            findings.append(
                err_finding(
                    "GV-001",
                    f"stateMachines.{machine.id}",
                    "state machine must have exactly one initial state",
                    "Set initialStateId to a single defined state",
                ),
            )
            continue
        if machine.initial_state_id not in machine.states:
            findings.append(
                err_finding(
                    "GV-001",
                    f"stateMachines.{machine.id}.initialStateId",
                    (
                        f"initial state '{machine.initial_state_id}' "
                        "is not defined in states map"
                    ),
                    "Define the initial state or update initialStateId",
                ),
            )
        seen_states: set[str] = set()
        for state_key, state in machine.states.items():
            if state.id != state_key:
                findings.append(
                    err_finding(
                        "GV-014",
                        f"stateMachines.{machine.id}.states",
                        f"duplicate state id '{state_key}'",
                        "Ensure state map keys match unique state ids",
                    ),
                )
            if state.id in seen_states:
                findings.append(
                    err_finding(
                        "GV-014",
                        f"stateMachines.{machine.id}.states",
                        f"duplicate state id '{state.id}'",
                        "Ensure state map keys match unique state ids",
                    ),
                )
            seen_states.add(state.id)
    root = game.session.root_machine_id
    if root and root not in game.state_machines:
        findings.append(
            err_finding(
                "GV-002",
                "session.rootMachineId",
                f"root machine '{root}' does not exist in stateMachines",
                "Set rootMachineId to an existing state machine id",
            ),
        )
    return findings
