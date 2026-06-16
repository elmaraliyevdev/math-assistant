"""Chain termination rules for single_chain mode."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.stack.execution_stack import ExecutionStack


def should_terminate_chain(
    *,
    effect: str,
    stack: ExecutionStack,
    game: GameVersion,
) -> bool:
    """Return True when a ``single_chain`` spin chain should stop."""
    if effect == "stay":
        return True
    frame = stack.top()
    if frame is None:
        return True
    root_machine_id = game.session.root_machine_id
    root_machine = game.state_machines[root_machine_id]
    if effect == "pop" and stack.depth == 1:
        return True
    if effect == "goto" and stack.depth == 1 and frame.machine_id == root_machine_id:
        return frame.state_id == root_machine.initial_state_id
    return False
