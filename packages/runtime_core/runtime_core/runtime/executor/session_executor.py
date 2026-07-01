"""SessionExecutor — deterministic spin chain execution loop (§8–§9)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from pathlib import Path

from runtime_core.common.paths import resolve_game_schema_root
from runtime_core.domain.game_version import GameVersion
from runtime_core.plugins.exceptions import PluginError
from runtime_core.runtime.events import EventContext, EventType
from runtime_core.runtime.events.payloads import FeatureCounterUpdatePayload
from runtime_core.runtime.exceptions import RuntimeError
from runtime_core.runtime.chain_metrics import ChainMetricsCollector
from runtime_core.runtime.executor.inheritance import inherit_spawn_context
from runtime_core.runtime.executor.multiplier import apply_frame_multiplier
from runtime_core.runtime.executor.plugin_manager import PluginManager
from runtime_core.runtime.executor.termination import should_terminate_chain
from runtime_core.runtime.executor.wins import apply_step_wins
from runtime_core.runtime.lifecycle import apply_transition
from runtime_core.runtime.plugins.counters import apply_step_side_effects
from runtime_core.runtime.plugins.host import PluginHost
from runtime_core.runtime.plugins.registry import PluginRegistry, default_builtin_registry
from runtime_core.runtime.session.factory import (
    SessionContext,
    new_session_context,
    new_session_params_from_request,
)
from runtime_core.runtime.spin_chain import (
    AccumulatorDelta,
    ChainFault,
    LimitHit,
    SpinChainRequest,
    SpinChainResult,
)
from runtime_core.runtime.stack import ExecutionStack
from runtime_core.runtime.stack.frame import StateMachineFrame
from runtime_core.runtime.transitions import resolve_transition
from runtime_core.validation.validators.priority_tiers import PriorityTierRegistry

_logger = logging.getLogger(__name__)
_TRACE_ENV = "RUNTIME_EXECUTOR_TRACE"


@dataclass(frozen=True, slots=True)
class SessionExecutorConfig:
    priority_tiers: PriorityTierRegistry | None = None
    plugin_registry: PluginRegistry | None = None
    game_schema_root: Path | None = None


class SessionExecutor:
    """Runtime Core execution loop for one spin chain."""

    def __init__(self, config: SessionExecutorConfig | None = None) -> None:
        cfg = config or SessionExecutorConfig()
        if cfg.priority_tiers is not None:
            self._tiers = cfg.priority_tiers
        else:
            schema_root = resolve_game_schema_root(schema_root=cfg.game_schema_root)
            self._tiers = PriorityTierRegistry.load(schema_root)
        registry = cfg.plugin_registry or default_builtin_registry()
        self._host = PluginHost(registry)

    def execute_spin_chain(self, req: SpinChainRequest) -> SpinChainResult:
        params = new_session_params_from_request(req)
        session = new_session_context(params)
        game = req.game
        stack = ExecutionStack(max_depth=game.session.max_stack_depth)
        plugins = PluginManager(
            self._host,
            game,
            total_bet_minor_units=session.total_bet_minor_units,
        )

        step_count = 0
        frame_push_count = 0
        chain_fault_count = 0
        limit_hit: LimitHit | None = None
        fault: ChainFault | None = None
        step_indices: dict[str, int] = {}
        multiplier_indices: dict[str, int] = {}
        metrics = ChainMetricsCollector()
        trace_enabled = os.environ.get(_TRACE_ENV, "").lower() in {"1", "true", "yes"}

        try:
            frame = stack.push_root(game)
            _emit_spin_chain_start(session, req.master_seed, session.total_bet_minor_units)
            handle = plugins.ensure_bound(frame)
            _emit_state_enter(session, stack, frame, game)

            terminated = False
            while not terminated and fault is None and limit_hit is None:
                frame = stack.top()
                if frame is None:
                    break
                if frame.frozen:
                    msg = "active frame is frozen; scheduler invariant violated"
                    fault = _runtime_fault(msg, frame)
                    break

                handle = plugins.ensure_bound(frame)
                step_index = step_indices.get(frame.frame_id, 0)
                frame_stream = session.chain_rng.frame_stream(frame.frame_id)
                step_rng = frame_stream.step_rng(step_index)
                step_indices[frame.frame_id] = step_index + 1

                try:
                    result = self._host.execute_step(handle, step_rng)
                except PluginError as exc:
                    fault = ChainFault(
                        code="PLUGIN_FAULT",
                        message=str(exc),
                        frame_id=frame.frame_id,
                        plugin_ref_id=handle.context.plugin_ref_id,
                    )
                    _emit_runtime_fault(session, fault)
                    break

                side_effects = apply_step_side_effects(frame.frame_context, result)
                _emit_step_events(session, stack, frame, result, side_effects.counter_events)
                metrics.record_trigger_tokens(result.trigger_tokens)

                wins = list(result.wins)
                multiplier_ref = _state_multiplier_ref(game, frame)
                if multiplier_ref and wins:
                    mult_index = multiplier_indices.get(frame.frame_id, 0)
                    wins, factor = apply_frame_multiplier(
                        game,
                        session,
                        multiplier_ref_id=multiplier_ref,
                        wins=wins,
                        frame_stream=frame_stream,
                        apply_index=mult_index,
                    )
                    multiplier_indices[frame.frame_id] = mult_index + 1
                    if factor is not None:
                        before = sum(int(w["winMinorUnits"]) for w in result.wins)
                        after = sum(int(w["winMinorUnits"]) for w in wins)
                        _sync_event_context(session, stack, frame)
                        session.events.emit(
                            EventType.MULTIPLIER_APPLIED,
                            {
                                "multiplierRefId": multiplier_ref,
                                "factor": factor,
                                "winMinorUnitsBefore": before,
                                "winMinorUnitsAfter": after,
                            },
                        )

                win_result = apply_step_wins(session, wins)
                metrics.record_wins(frame.rtp_category, wins)
                metrics.record_win_symbols(wins)
                grid = result.grid_outcome
                if isinstance(grid, dict) and isinstance(grid.get("symbols"), list):
                    metrics.record_grid(frame.rtp_category, grid["symbols"])
                if wins:
                    _emit_win_evaluated(session, stack, frame, wins)
                if win_result.cap_applied:
                    _sync_event_context(session, stack, frame)
                    session.events.emit(
                        EventType.EXPOSURE_CAP_APPLIED,
                        {
                            "capMinorUnits": session.exposure.effective_cap_minor,
                            "uncappedWinMinorUnits": win_result.uncapped_total,
                        },
                    )

                tokens = list(result.trigger_tokens)
                step_complete = bool(tokens)
                resolve_result = resolve_transition(
                    game,
                    frame,
                    tokens,
                    self._tiers,
                    step_complete=step_complete,
                )
                if resolve_result.fault is not None:
                    fault = resolve_result.fault
                    _emit_runtime_fault(session, fault)
                    break

                if resolve_result.continue_multistep:
                    if trace_enabled:
                        _record_trace_step(
                            metrics,
                            step_count=step_count,
                            stack=stack,
                            frame=frame,
                            result=result,
                            tokens=tokens,
                            transition=None,
                        )
                    step_count += 1
                    limit_hit = _check_limits(session, step_count, frame_push_count)
                    if limit_hit is not None:
                        _emit_limit_hit(session, limit_hit)
                    continue

                assert resolve_result.resolution is not None
                resolution = resolve_result.resolution
                chain_fault_count += len(resolution.warnings)

                prior_frame_id = frame.frame_id
                try:
                    outcome = apply_transition(
                        stack,
                        game,
                        frame,
                        resolution.transition,
                        warnings=resolution.warnings,
                    )
                except RuntimeError as exc:
                    fault = ChainFault(
                        code="LIFECYCLE_FAULT",
                        message=str(exc),
                        frame_id=frame.frame_id,
                    )
                    _emit_runtime_fault(session, fault)
                    break

                if outcome.fault is not None:
                    fault = outcome.fault
                    chain_fault_count += len(outcome.warnings)
                    _emit_runtime_fault(session, fault)
                    break

                chain_fault_count += len(outcome.warnings)
                _emit_transition_taken(session, stack, frame, resolution.transition)

                if trace_enabled:
                    _record_trace_step(
                        metrics,
                        step_count=step_count,
                        stack=stack,
                        frame=frame,
                        result=result,
                        tokens=tokens,
                        transition=resolution.transition,
                    )
                    _logger.info(
                        "fsm_transition",
                        extra={
                            "transition_id": resolution.transition.id,
                            "trigger": resolution.transition.trigger,
                            "effect": resolution.transition.effect,
                            "target_state_id": resolution.transition.target_state_id,
                            "target_machine_id": resolution.transition.target_machine_id,
                            "stack_depth": stack.depth,
                            "stack_machines": [f.machine_id for f in stack.frames],
                        },
                    )

                active = stack.top()
                if active is None:
                    terminated = True
                    break

                if outcome.effect == "goto":
                    plugins.release_frame(prior_frame_id)
                    _emit_state_enter(session, stack, active, game)
                elif outcome.effect == "spawn":
                    parent = stack.parent()
                    if parent is not None:
                        inherit_spawn_context(parent.frame_context, active.frame_context)
                    frame_push_count += 1
                    metrics.record_nested_spawn()
                    _emit_frame_push(session, stack, parent, outcome.pushed_frame)
                    _emit_state_enter(session, stack, active, game)
                elif outcome.effect == "pop":
                    if outcome.popped_frame is not None:
                        plugins.release_frame(outcome.popped_frame.frame_id)
                    _emit_frame_pop(session, stack, outcome.popped_frame, active)
                    _emit_state_reenter(session, stack, active, game)

                if should_terminate_chain(
                    effect=outcome.effect,
                    stack=stack,
                    game=game,
                ):
                    terminated = True

                step_count += 1
                limit_hit = _check_limits(session, step_count, frame_push_count)
                if limit_hit is not None:
                    _emit_limit_hit(session, limit_hit)
                    break

        finally:
            plugins.release_all()

        _emit_spin_chain_end(session, step_count)

        return SpinChainResult(
            total_win_minor_units=session.total_win_minor_units,
            total_uncapped_win_minor_units=session.total_uncapped_win_minor_units,
            total_truncated_minor_units=session.total_truncated_minor_units,
            total_bet_minor_units=session.total_bet_minor_units,
            step_count=step_count,
            frame_push_count=frame_push_count,
            exposure_cap_applied=session.exposure_cap_applied,
            limit_hit=limit_hit,
            fault=fault,
            events=session.events.events,
            event_log_hash=session.events.replay_hash,
            accumulator_delta=AccumulatorDelta(
                capped_win_minor_units=session.total_win_minor_units,
                uncapped_win_minor_units=session.total_uncapped_win_minor_units,
                exposure_truncation_count=1 if session.exposure_cap_applied else 0,
                exposure_truncated_minor_units=session.total_truncated_minor_units,
                chain_fault_count=chain_fault_count,
            ),
            chain_metrics=metrics.freeze(),
        )


def execute_spin_chain(req: SpinChainRequest) -> SpinChainResult:
    """Execute one spin chain using the default SessionExecutor."""
    return SessionExecutor().execute_spin_chain(req)


def _state_multiplier_ref(game: GameVersion, frame: StateMachineFrame) -> str | None:
    state = game.state_machines[frame.machine_id].states[frame.state_id]
    ref = state.plugin_config.get("multiplierRefId")
    return str(ref) if isinstance(ref, str) and ref else None


def _check_limits(
    session: SessionContext,
    step_count: int,
    frame_push_count: int,
) -> LimitHit | None:
    limits = session.limits
    if step_count > limits.max_steps_per_spin_chain:
        return LimitHit(code="MAX_STEPS_PER_SPIN_CHAIN", action="abort")
    if len(session.events.events) > limits.max_events_per_chain:
        return LimitHit(code="MAX_EVENTS_PER_CHAIN", action="abort")
    if frame_push_count > limits.max_frames_per_chain:
        return LimitHit(code="MAX_FRAMES_PER_CHAIN", action="abort")
    return None


def _sync_event_context(
    session: SessionContext,
    stack: ExecutionStack,
    frame: StateMachineFrame,
) -> None:
    session.events.set_context(
        EventContext(
            stack_depth=stack.depth,
            machine_id=frame.machine_id,
            state_id=frame.state_id,
            frame_id=frame.frame_id,
        ),
    )


def _emit_spin_chain_start(
    session: SessionContext,
    master_seed: bytes,
    bet_minor_units: int,
) -> None:
    session.events.set_context(
        EventContext(stack_depth=0, machine_id="", state_id="", frame_id=""),
    )
    session.events.emit(
        EventType.SPIN_CHAIN_START,
        {
            "masterSeed": master_seed.hex(),
            "betMinorUnits": bet_minor_units,
        },
    )


def _emit_spin_chain_end(session: SessionContext, step_count: int) -> None:
    session.events.emit(
        EventType.SPIN_CHAIN_END,
        {
            "totalWinMinorUnits": session.total_win_minor_units,
            "stepCount": step_count,
        },
    )


def _emit_state_enter(
    session: SessionContext,
    stack: ExecutionStack,
    frame: StateMachineFrame,
    game: GameVersion,
) -> None:
    state = game.state_machines[frame.machine_id].states[frame.state_id]
    _sync_event_context(session, stack, frame)
    session.events.emit(
        EventType.STATE_ENTER,
        {
            "stateId": frame.state_id,
            "pluginRefId": state.plugin_ref_id,
            "rtpCategory": frame.rtp_category,
        },
    )


def _emit_state_reenter(
    session: SessionContext,
    stack: ExecutionStack,
    frame: StateMachineFrame,
    game: GameVersion,
) -> None:
    state = game.state_machines[frame.machine_id].states[frame.state_id]
    _sync_event_context(session, stack, frame)
    session.events.emit(
        EventType.STATE_REENTER,
        {
            "stateId": frame.state_id,
            "pluginRefId": state.plugin_ref_id,
            "rtpCategory": frame.rtp_category,
        },
    )


def _emit_step_events(
    session: SessionContext,
    stack: ExecutionStack,
    frame: StateMachineFrame,
    result,
    counter_events: list[FeatureCounterUpdatePayload],
) -> None:
    _sync_event_context(session, stack, frame)
    grid = result.grid_outcome
    if isinstance(grid, dict) and "symbols" in grid:
        session.events.emit(
            EventType.GRID_RESULT,
            {
                "reelSetId": str(grid["reelSetId"]),
                "symbols": grid["symbols"],
                "rngDrawIds": list(grid.get("rngDrawIds", [])),
            },
        )
    if result.trigger_tokens:
        session.events.emit(
            EventType.TRIGGER_EMITTED,
            {"tokens": list(result.trigger_tokens)},
        )
    for counter in counter_events:
        session.events.emit(
            EventType.FEATURE_COUNTER_UPDATE,
            counter.model_dump(mode="json", by_alias=True),
        )


def _emit_win_evaluated(
    session: SessionContext,
    stack: ExecutionStack,
    frame: StateMachineFrame,
    wins: list[dict[str, object]],
) -> None:
    components = [
        {
            "source": str(win["source"]),
            "symbolId": str(win.get("symbolId", "")),
            "count": int(win.get("count", 0)),
            "winMinorUnits": int(win["winMinorUnits"]),
        }
        for win in wins
    ]
    total = sum(int(c["winMinorUnits"]) for c in components)
    _sync_event_context(session, stack, frame)
    session.events.emit(
        EventType.WIN_EVALUATED,
        {
            "rtpCategory": frame.rtp_category,
            "components": components,
            "totalWinMinorUnits": total,
        },
    )


def _emit_transition_taken(session, stack, frame, transition) -> None:
    _sync_event_context(session, stack, frame)
    session.events.emit(
        EventType.TRANSITION_TAKEN,
        {
            "transitionId": transition.id,
            "trigger": transition.trigger,
            "effect": transition.effect,
            "targetMachineId": transition.target_machine_id,
            "priority": transition.priority,
            "priorityTier": transition.priority_tier or "",
            "candidatesRejected": [],
        },
    )


def _emit_frame_push(session, stack, parent, child) -> None:
    if parent is None or child is None:
        return
    _sync_event_context(session, stack, child)
    session.events.emit(
        EventType.FRAME_PUSH,
        {
            "targetMachineId": child.machine_id,
            "parentFrameId": parent.frame_id,
            "newFrameId": child.frame_id,
        },
    )


def _emit_frame_pop(session, stack, popped, resumed) -> None:
    if popped is None or resumed is None:
        return
    _sync_event_context(session, stack, resumed)
    session.events.emit(
        EventType.FRAME_POP,
        {
            "frameId": popped.frame_id,
            "resumedFrameId": resumed.frame_id,
            "machineId": popped.machine_id,
        },
    )


def _emit_limit_hit(session: SessionContext, limit_hit: LimitHit) -> None:
    session.events.emit(
        EventType.RUNTIME_LIMIT_HIT,
        {"limitCode": limit_hit.code, "action": limit_hit.action},
    )


def _emit_runtime_fault(session: SessionContext, fault: ChainFault) -> None:
    session.events.emit(
        EventType.RUNTIME_FAULT,
        {"faultCode": fault.code, "message": fault.message},
    )


def _runtime_fault(message: str, frame: StateMachineFrame) -> ChainFault:
    return ChainFault(
        code="RUNTIME_FAULT",
        message=message,
        frame_id=frame.frame_id,
    )


def _record_trace_step(
    metrics: ChainMetricsCollector,
    *,
    step_count: int,
    stack: ExecutionStack,
    frame: StateMachineFrame,
    result,
    tokens: list[str],
    transition,
) -> None:
    scatter_counts = result.frame_local_patch.get("scatterCounts", {})
    metrics.record_trace_step(
        {
            "step": step_count,
            "machineId": frame.machine_id,
            "stateId": frame.state_id,
            "stackDepth": stack.depth,
            "stackMachines": [f.machine_id for f in stack.frames],
            "scatterCounts": scatter_counts if isinstance(scatter_counts, dict) else {},
            "triggerTokens": list(tokens),
            "transition": (
                {
                    "id": transition.id,
                    "trigger": transition.trigger,
                    "effect": transition.effect,
                    "targetStateId": transition.target_state_id,
                    "targetMachineId": transition.target_machine_id,
                }
                if transition is not None
                else None
            ),
        },
    )
    if tokens:
        _logger.debug(
            "trigger_emitted",
            extra={
                "step": step_count,
                "state_id": frame.state_id,
                "tokens": tokens,
                "scatter_counts": scatter_counts,
            },
        )
