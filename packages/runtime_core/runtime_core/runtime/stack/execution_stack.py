"""Execution stack push/pop/freeze/resume operations."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.domain.game_version import GameVersion
from runtime_core.domain.state_machine import State, StateMachine
from runtime_core.runtime.exceptions import RuntimeError
from runtime_core.runtime.frames import FrameContext
from runtime_core.runtime.stack.frame import StateMachineFrame, build_frame


class StackLimitError(RuntimeError):
    """Stack depth would exceed configured limit."""


@dataclass
class ExecutionStack:
    """Ordered stack of state machine frames (ADR-004)."""

    max_depth: int
    _frames: list[StateMachineFrame] = field(default_factory=list)
    _push_sequence: int = 0

    @property
    def depth(self) -> int:
        return len(self._frames)

    @property
    def frames(self) -> tuple[StateMachineFrame, ...]:
        return tuple(self._frames)

    def top(self) -> StateMachineFrame | None:
        if not self._frames:
            return None
        return self._frames[-1]

    def parent(self) -> StateMachineFrame | None:
        if len(self._frames) < 2:
            return None
        return self._frames[-2]

    def push_root(self, game: GameVersion) -> StateMachineFrame:
        if self._frames:
            msg = "push_root requires empty stack"
            raise RuntimeError(msg)
        machine = _machine(game, game.session.root_machine_id)
        state = machine.states[machine.initial_state_id]
        frame = self._push_frame(
            machine_id=machine.id,
            state=state,
            frozen=False,
        )
        return frame

    def push_child(
        self,
        game: GameVersion,
        target_machine_id: str,
        *,
        frame_context: FrameContext | None = None,
    ) -> StateMachineFrame:
        if not self._frames:
            msg = "push_child requires active parent frame"
            raise RuntimeError(msg)
        if self.depth >= self.max_depth:
            msg = (
                f"stack depth {self.depth} would exceed "
                f"maxStackDepth {self.max_depth}"
            )
            raise StackLimitError(msg)
        self.freeze_top()
        machine = _machine(game, target_machine_id)
        state = machine.states[machine.initial_state_id]
        frame = self._push_frame(
            machine_id=machine.id,
            state=state,
            frame_context=frame_context,
            frozen=False,
        )
        return frame

    def pop(self) -> StateMachineFrame:
        if len(self._frames) <= 1:
            msg = "pop requires stack depth > 1"
            raise RuntimeError(msg)
        popped = self._frames.pop()
        self.resume_parent()
        return popped

    def freeze_top(self) -> None:
        if len(self._frames) >= 1:
            self._frames[-1].frozen = True

    def resume_parent(self) -> None:
        if self._frames:
            self._frames[-1].frozen = False

    def replace_top(self, frame: StateMachineFrame) -> None:
        if not self._frames:
            msg = "cannot replace top frame on empty stack"
            raise RuntimeError(msg)
        self._frames[-1] = frame

    def _push_frame(
        self,
        *,
        machine_id: str,
        state: State,
        frame_context: FrameContext | None = None,
        frozen: bool,
    ) -> StateMachineFrame:
        stack_index = len(self._frames)
        frame_id = f"f-{stack_index}-{self._push_sequence}"
        self._push_sequence += 1
        frame = build_frame(
            frame_id=frame_id,
            machine_id=machine_id,
            state=state,
            frame_context=frame_context,
            frozen=frozen,
        )
        self._frames.append(frame)
        return frame


def _machine(game: GameVersion, machine_id: str) -> StateMachine:
    machine = game.state_machines.get(machine_id)
    if machine is None:
        msg = f"unknown state machine {machine_id!r}"
        raise RuntimeError(msg)
    return machine
