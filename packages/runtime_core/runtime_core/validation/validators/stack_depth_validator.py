"""Worst-case spawn stack depth validation."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.validation.validators.finding import Finding, err_finding


def validate_stack_depth(game: GameVersion | None) -> list[Finding]:
    findings: list[Finding] = []
    if game is None:
        return findings
    root = game.session.root_machine_id
    if not root:
        return findings
    worst = worst_case_stack_depth(game, root, {})
    limit = game.session.max_stack_depth or 8
    if worst > limit:
        findings.append(
            err_finding(
                "GV-012",
                "session.maxStackDepth",
                "worst-case spawn stack depth exceeds maxStackDepth",
                (
                    "Increase maxStackDepth or reduce nested spawn depth "
                    f"(worst case: {worst}, limit: {limit})"
                ),
            ),
        )
    return findings


def worst_case_stack_depth(
    game: GameVersion,
    machine_id: str,
    memo: dict[str, int],
) -> int:
    cached = memo.get(machine_id)
    if cached is not None:
        return cached
    machine = game.state_machines.get(machine_id)
    if machine is None:
        memo[machine_id] = 1
        return 1
    max_child_depth = 0
    for state in machine.states.values():
        for transition in state.transitions:
            if transition.effect != "spawn" or not transition.target_machine_id:
                continue
            child_depth = worst_case_stack_depth(
                game, transition.target_machine_id, memo
            )
            max_child_depth = max(max_child_depth, child_depth)
    depth = 1 + max_child_depth if max_child_depth > 0 else 1
    memo[machine_id] = depth
    return depth
