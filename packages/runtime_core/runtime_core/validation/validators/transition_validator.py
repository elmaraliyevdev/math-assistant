"""Transition target, priority, and conflict validation."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.state_machine import State, Transition
from runtime_core.validation.validators.finding import (
    Finding,
    err_finding,
    warn_finding,
)
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry


def validate_transitions(
    game: GameVersion | None,
    tiers: PriorityTierRegistry | None,
) -> list[Finding]:
    findings: list[Finding] = []
    if game is None:
        return findings
    for machine_id, machine in game.state_machines.items():
        for state_id, state in machine.states.items():
            seen_transition_ids: set[str] = set()
            for transition in state.transitions:
                if transition.id in seen_transition_ids:
                    findings.append(
                        err_finding(
                            "GV-013",
                            f"stateMachines.{machine_id}.states.{state_id}.transitions",
                            f"duplicate transition id '{transition.id}' within state",
                            "Assign unique transition ids per state",
                        ),
                    )
                seen_transition_ids.add(transition.id)
                path = _transition_path(machine_id, state_id, transition.id)
                findings.extend(
                    _validate_transition_targets(game, machine_id, path, transition)
                )
                if tiers is not None:
                    findings.extend(_validate_priority_tier(tiers, path, transition))
            findings.extend(
                _validate_transition_conflicts(game, machine_id, state_id, state)
            )
    return findings


def _transition_path(machine_id: str, state_id: str, transition_id: str) -> str:
    return f"stateMachines.{machine_id}.states.{state_id}.transitions.{transition_id}"


def _validate_transition_targets(
    game: GameVersion,
    machine_id: str,
    path: str,
    transition: Transition,
) -> list[Finding]:
    findings: list[Finding] = []
    machine = game.state_machines[machine_id]
    effect = transition.effect
    if effect in {"goto", "stay"}:
        target = transition.target_state_id
        if target and target not in machine.states:
            findings.append(
                err_finding(
                    "GV-003",
                    path,
                    (
                        f"transition target state '{target}' does not exist "
                        f"in machine '{machine_id}'"
                    ),
                    "Point targetStateId to an existing state or remove the transition",
                ),
            )
    elif effect == "spawn":
        target = transition.target_machine_id
        if target and target not in game.state_machines:
            findings.append(
                err_finding(
                    "GV-004",
                    path,
                    f"spawn target machine '{target}' does not exist",
                    "Define the nested machine or fix targetMachineId",
                ),
            )
    elif effect == "pop":
        if transition.target_state_id or transition.target_machine_id:
            findings.append(
                err_finding(
                    "GV-010",
                    path,
                    "pop effect must not specify targetStateId or targetMachineId",
                    "Remove target fields from pop transitions",
                ),
            )
    return findings


def _validate_priority_tier(
    tiers: PriorityTierRegistry,
    path: str,
    transition: Transition,
) -> list[Finding]:
    if not transition.priority_tier:
        return [
            warn_finding(
                "GV-028",
                path,
                "transition is missing priorityTier",
                "Set priorityTier to a registered tier for deterministic ordering",
            ),
        ]
    tier = tiers.resolve(transition.priority_tier)
    if tier is None:
        return [
            err_finding(
                "GV-027",
                path,
                f"unknown priorityTier '{transition.priority_tier}'",
                "Use a tier from priority-tiers-v1.json",
            ),
        ]
    if (
        transition.priority != tier.default_priority
        and (
            transition.priority < tier.range_min
            or transition.priority > tier.range_max
        )
    ):
            return [
                err_finding(
                    "GV-027",
                    path,
                    f"priority is outside allowed range for tier '{tier.id}'",
                    "Set priority within the tier numericRange or use defaultPriority",
                ),
            ]
    return []


@dataclass(frozen=True, slots=True)
class _TransitionGroupKey:
    trigger: str
    priority: int
    tier: str


def _validate_transition_conflicts(
    game: GameVersion,
    machine_id: str,
    state_id: str,
    state: State,
) -> list[Finding]:
    findings: list[Finding] = []
    groups: dict[_TransitionGroupKey, list[Transition]] = {}
    for transition in state.transitions:
        key = _TransitionGroupKey(
            trigger=transition.trigger,
            priority=transition.priority,
            tier=transition.priority_tier or "",
        )
        groups.setdefault(key, []).append(transition)
    base_path = f"stateMachines.{machine_id}.states.{state_id}.transitions"
    for key, group in groups.items():
        if len(group) <= 1:
            continue
        findings.append(
            warn_finding(
                "GV-016",
                base_path,
                (
                    f"multiple transitions share trigger '{key.trigger}' "
                    "with identical priority and tier"
                ),
                "Differentiate priority or priorityTier to resolve ambiguity",
            ),
        )
        if not _resolvable_by_precedence(game, group):
            findings.append(
                err_finding(
                    "GV-017",
                    base_path,
                    (
                        f"ambiguous transition set for trigger '{key.trigger}' "
                        "cannot be resolved by precedence"
                    ),
                    "Adjust priorities or precedence.triggerOrder",
                ),
            )
    return findings


def _resolvable_by_precedence(game: GameVersion, transitions: list[Transition]) -> bool:
    if len(transitions) <= 1:
        return True
    order = game.precedence.trigger_order
    if not order:
        return False
    rank = {trigger: index for index, trigger in enumerate(order)}
    best_rank = len(order) + 1
    for transition in transitions:
        trigger_rank = rank.get(transition.trigger)
        if trigger_rank is None:
            return False
        best_rank = min(best_rank, trigger_rank)
    count_best = sum(1 for tr in transitions if rank[tr.trigger] == best_rank)
    return count_best == 1
