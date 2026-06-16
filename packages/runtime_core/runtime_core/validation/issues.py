"""Validation error code constructors (SV-* and GV-*)."""

from __future__ import annotations

from runtime_core.validation.report import Severity, ValidationFinding


def _issue(
    code: str,
    path: str,
    message: str,
    suggestion: str,
    *,
    severity: Severity,
) -> ValidationFinding:
    return ValidationFinding(
        code=code,
        severity=severity,
        path=path,
        message=message,
        suggestion=suggestion,
    )


def err_issue(code: str, path: str, message: str, suggestion: str) -> ValidationFinding:
    return _issue(code, path, message, suggestion, severity=Severity.ERROR)


def warn_issue(
    code: str, path: str, message: str, suggestion: str
) -> ValidationFinding:
    return _issue(code, path, message, suggestion, severity=Severity.WARNING)


# Schema issue helpers (SV-xxx)


def schema_required(path: str, field: str) -> ValidationFinding:
    return err_issue(
        "SV-001",
        path,
        f"required property missing: {field}",
        "Add the required field to satisfy the canonical schema",
    )


def schema_type(path: str, expected: str) -> ValidationFinding:
    return err_issue(
        "SV-002",
        path,
        f"value has incorrect type; expected {expected}",
        "Correct the value type to match the schema definition",
    )


def schema_enum(path: str, allowed: str) -> ValidationFinding:
    return err_issue(
        "SV-003",
        path,
        "value is not in allowed enum",
        f"Use one of: {allowed}",
    )


def schema_pattern(path: str) -> ValidationFinding:
    return err_issue(
        "SV-004",
        path,
        "value does not match required pattern",
        "Adjust the value to match the schema pattern constraint",
    )


def schema_range(path: str, detail: str) -> ValidationFinding:
    return err_issue(
        "SV-005",
        path,
        f"numeric constraint violated: {detail}",
        "Adjust the numeric value to fall within schema bounds",
    )


def schema_additional_property(path: str, prop: str) -> ValidationFinding:
    return err_issue(
        "SV-006",
        path,
        f"additional property not allowed: {prop}",
        "Remove the unknown property or move it to extensions",
    )


def schema_generic(path: str, message: str) -> ValidationFinding:
    return err_issue(
        "SV-001",
        path,
        message,
        "Fix the document to conform to game-version-1.0.0.schema.json",
    )


def schema_invalid_json(message: str) -> ValidationFinding:
    return err_issue(
        "SV-002",
        "$",
        f"document is not valid JSON: {message}",
        "Provide well-formed JSON",
    )


# Graph issue helpers (GV-xxx)


def graph_initial_state_missing(machine_id: str, state_id: str) -> ValidationFinding:
    return err_issue(
        "GV-001",
        f"stateMachines.{machine_id}.initialStateId",
        f"initial state '{state_id}' is not defined in states map",
        "Define the initial state or update initialStateId",
    )


def graph_root_machine_missing(machine_id: str) -> ValidationFinding:
    return err_issue(
        "GV-002",
        "session.rootMachineId",
        f"root machine '{machine_id}' does not exist in stateMachines",
        "Set rootMachineId to an existing state machine id",
    )


def graph_transition_target_missing(
    machine_id: str,
    state_id: str,
    transition_id: str,
    target: str,
) -> ValidationFinding:
    return err_issue(
        "GV-003",
        f"stateMachines.{machine_id}.states.{state_id}.transitions.{transition_id}",
        f"transition target state '{target}' does not exist in machine '{machine_id}'",
        "Point targetStateId to an existing state or remove the transition",
    )


def graph_spawn_target_missing(
    machine_id: str,
    state_id: str,
    transition_id: str,
    target: str,
) -> ValidationFinding:
    return err_issue(
        "GV-004",
        f"stateMachines.{machine_id}.states.{state_id}.transitions.{transition_id}",
        f"spawn target machine '{target}' does not exist",
        "Define the nested machine or fix targetMachineId",
    )


def graph_orphan_state(machine_id: str, state_id: str) -> ValidationFinding:
    return err_issue(
        "GV-005",
        f"stateMachines.{machine_id}.states.{state_id}",
        "state is unreachable from the session entry point",
        "Add transitions that reach this state or mark it deprecated",
    )


def graph_dead_end(machine_id: str, state_id: str) -> ValidationFinding:
    return err_issue(
        "GV-006",
        f"stateMachines.{machine_id}.states.{state_id}",
        "non-terminal state has no outgoing transitions",
        "Add transitions or mark the state terminal",
    )


def graph_spawn_no_pop(machine_id: str) -> ValidationFinding:
    return err_issue(
        "GV-008",
        f"stateMachines.{machine_id}",
        "spawned machine has no pop transition path to return to parent",
        "Add a FEATURE_COMPLETE transition with effect pop",
    )


def graph_infinite_loop(machine_id: str, state_id: str) -> ValidationFinding:
    return err_issue(
        "GV-011",
        f"stateMachines.{machine_id}.states.{state_id}",
        "infinite progression loop detected without terminating progression metadata",
        "Add progression metadata or a terminating transition",
    )


def graph_stack_depth_exceeded(worst_case: int, limit: int) -> ValidationFinding:
    return err_issue(
        "GV-012",
        "session.maxStackDepth",
        "worst-case spawn stack depth exceeds maxStackDepth",
        (
            "Increase maxStackDepth or reduce nested spawn depth "
            f"(worst case: {worst_case}, limit: {limit})"
        ),
    )


def graph_duplicate_transition_id(
    machine_id: str,
    state_id: str,
    transition_id: str,
) -> ValidationFinding:
    return err_issue(
        "GV-013",
        f"stateMachines.{machine_id}.states.{state_id}.transitions",
        f"duplicate transition id '{transition_id}' within state",
        "Assign unique transition ids per state",
    )


def graph_duplicate_state_id(machine_id: str, state_id: str) -> ValidationFinding:
    return err_issue(
        "GV-014",
        f"stateMachines.{machine_id}.states",
        f"duplicate state id '{state_id}'",
        "Ensure state map keys match unique state ids",
    )


def graph_duplicate_machine_id(machine_id: str) -> ValidationFinding:
    return err_issue(
        "GV-015",
        "stateMachines",
        f"duplicate state machine id '{machine_id}'",
        "Ensure machine map keys match unique machine ids",
    )


def graph_priority_conflict(
    machine_id: str, state_id: str, trigger: str
) -> ValidationFinding:
    return warn_issue(
        "GV-016",
        f"stateMachines.{machine_id}.states.{state_id}.transitions",
        f"multiple transitions share trigger '{trigger}' with identical priority and tier",
        "Differentiate priority or priorityTier to resolve ambiguity",
    )


def graph_ambiguous_transitions(
    machine_id: str,
    state_id: str,
    trigger: str,
) -> ValidationFinding:
    return err_issue(
        "GV-017",
        f"stateMachines.{machine_id}.states.{state_id}.transitions",
        f"ambiguous transition set for trigger '{trigger}' cannot be resolved by precedence",
        "Adjust priorities or precedence.triggerOrder",
    )


def graph_plugin_ref_missing(state_path: str, ref_id: str) -> ValidationFinding:
    return err_issue(
        "GV-018",
        state_path,
        f"pluginRefId '{ref_id}' does not exist in plugins registry",
        "Define the plugin reference or fix pluginRefId",
    )


def graph_plugin_version_unsupported(
    ref_id: str,
    plugin_id: str,
    version: str,
) -> ValidationFinding:
    return err_issue(
        "GV-019",
        f"plugins.{ref_id}",
        f"plugin version '{version}' is not supported for {plugin_id}",
        "Use a supported plugin version (MVP: 1.0.0)",
    )


def graph_plugin_capability_missing(ref_id: str, capability: str) -> ValidationFinding:
    return err_issue(
        "GV-020",
        f"plugins.{ref_id}",
        f"required capability '{capability}' is not declared",
        "Add the capability to the plugin reference",
    )


def graph_plugin_symbol_missing(path: str, symbol_id: str) -> ValidationFinding:
    return err_issue(
        "GV-021",
        path,
        f"symbol '{symbol_id}' referenced in plugin config does not exist",
        "Define the symbol in symbols or fix the reference",
    )


def graph_plugin_reel_mismatch(
    path: str, expected: int, actual: int
) -> ValidationFinding:
    return err_issue(
        "GV-022",
        path,
        "reel set reel count does not match game grid",
        f"Ensure reel set has {expected} reels (found {actual})",
    )


def graph_exposure_cap_exceeded(theoretical: int, cap: int) -> ValidationFinding:
    return err_issue(
        "GV-023",
        "exposure",
        "theoretical max win exceeds effective exposure cap",
        (
            "Raise exposure caps or reduce paytable/jackpot potential "
            f"(theoretical: {theoretical}, cap: {cap})"
        ),
    )


def graph_rtp_category_unknown(state_path: str, category: str) -> ValidationFinding:
    return err_issue(
        "GV-025",
        state_path,
        f"rtpCategory '{category}' is not registered",
        "Use a platform or document registry category id",
    )


def graph_priority_tier_unknown(transition_path: str, tier: str) -> ValidationFinding:
    return err_issue(
        "GV-027",
        transition_path,
        f"unknown priorityTier '{tier}'",
        "Use a tier from priority-tiers-v1.json",
    )


def graph_priority_tier_missing(transition_path: str) -> ValidationFinding:
    return warn_issue(
        "GV-028",
        transition_path,
        "transition is missing priorityTier",
        "Set priorityTier to a registered tier for deterministic ordering",
    )


def graph_priority_out_of_range(transition_path: str, tier: str) -> ValidationFinding:
    return err_issue(
        "GV-027",
        transition_path,
        f"priority is outside allowed range for tier '{tier}'",
        "Set priority within the tier numericRange or use defaultPriority",
    )


def graph_invalid_pop(transition_path: str) -> ValidationFinding:
    return err_issue(
        "GV-010",
        transition_path,
        "pop effect must not specify targetStateId or targetMachineId",
        "Remove target fields from pop transitions",
    )


def graph_multiple_initial_states(machine_id: str) -> ValidationFinding:
    return err_issue(
        "GV-001",
        f"stateMachines.{machine_id}",
        "state machine must have exactly one initial state",
        "Set initialStateId to a single defined state",
    )


def graph_plugin_config_invalid(path: str, detail: str) -> ValidationFinding:
    return err_issue(
        "GV-021",
        path,
        f"plugin configuration failed schema validation: {detail}",
        "Fix pluginConfig to match the plugin schema",
    )


def graph_exposure_multiplier_invalid() -> ValidationFinding:
    return err_issue(
        "GV-023",
        "exposure.maxWinMultiplier",
        "maxWinMultiplier must be greater than 0 in strict mode",
        "Set a positive maxWinMultiplier or remove enforceCap",
    )


def graph_exposure_cap_invalid() -> ValidationFinding:
    return err_issue(
        "GV-023",
        "exposure.maxWinMinorUnits",
        "maxWinMinorUnits must be greater than 0 when enforceCap is true",
        "Set a positive exposure cap in minor units",
    )


def graph_exposure_scope_invalid(scope: str) -> ValidationFinding:
    return err_issue(
        "GV-023",
        "exposure.capScope",
        f"invalid capScope '{scope}'",
        "Use session_spin_chain, feature_instance, or spin_step",
    )


def graph_limits_frames_exceed_stack(frames: int, stack: int) -> ValidationFinding:
    return err_issue(
        "GV-036",
        "session.runtimeLimits.maxFramesPerChain",
        "maxFramesPerChain exceeds maxStackDepth",
        f"Set maxFramesPerChain <= maxStackDepth ({stack})",
    )


def graph_limits_respins_exceeded(
    path: str, respins: int, limit: int
) -> ValidationFinding:
    return err_issue(
        "GV-037",
        path,
        "initialRespins exceeds maxRespinsPerFeature",
        f"Reduce initialRespins to {limit} or raise runtime limit",
    )
