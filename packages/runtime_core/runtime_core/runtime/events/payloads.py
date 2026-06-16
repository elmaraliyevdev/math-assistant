"""Frozen MVP event payload contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class _FrozenPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class SpinChainStartPayload(_FrozenPayload):
    master_seed: str = Field(alias="masterSeed")
    bet_minor_units: int = Field(alias="betMinorUnits")


class SpinChainEndPayload(_FrozenPayload):
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")
    step_count: int = Field(alias="stepCount")


class FramePushPayload(_FrozenPayload):
    target_machine_id: str = Field(alias="targetMachineId")
    parent_frame_id: str = Field(alias="parentFrameId")
    new_frame_id: str = Field(alias="newFrameId")


class FramePopPayload(_FrozenPayload):
    frame_id: str = Field(alias="frameId")
    resumed_frame_id: str = Field(alias="resumedFrameId")
    machine_id: str = Field(alias="machineId")


class StateEnterPayload(_FrozenPayload):
    state_id: str = Field(alias="stateId")
    plugin_ref_id: str | None = Field(default=None, alias="pluginRefId")
    rtp_category: str = Field(alias="rtpCategory")


class StateReenterPayload(_FrozenPayload):
    state_id: str = Field(alias="stateId")
    plugin_ref_id: str | None = Field(default=None, alias="pluginRefId")
    rtp_category: str = Field(alias="rtpCategory")


class GridResultPayload(_FrozenPayload):
    reel_set_id: str = Field(alias="reelSetId")
    symbols: list[list[str]]
    rng_draw_ids: list[int] = Field(alias="rngDrawIds")


class WinComponent(_FrozenPayload):
    source: str
    symbol_id: str = Field(alias="symbolId")
    count: int
    win_minor_units: int = Field(alias="winMinorUnits")


class WinEvaluatedPayload(_FrozenPayload):
    rtp_category: str = Field(alias="rtpCategory")
    components: list[WinComponent]
    total_win_minor_units: int = Field(alias="totalWinMinorUnits")


class TriggerEmittedPayload(_FrozenPayload):
    tokens: list[str]


class TransitionTakenPayload(_FrozenPayload):
    transition_id: str = Field(alias="transitionId")
    trigger: str
    effect: str
    target_machine_id: str | None = Field(default=None, alias="targetMachineId")
    priority: int
    priority_tier: str = Field(alias="priorityTier")
    candidates_rejected: list[str] = Field(
        default_factory=list,
        alias="candidatesRejected",
    )


class MultiplierAppliedPayload(_FrozenPayload):
    multiplier_ref_id: str = Field(alias="multiplierRefId")
    factor: int | float
    win_minor_units_before: int = Field(alias="winMinorUnitsBefore")
    win_minor_units_after: int = Field(alias="winMinorUnitsAfter")


class ExposureCapAppliedPayload(_FrozenPayload):
    cap_minor_units: int = Field(alias="capMinorUnits")
    uncapped_win_minor_units: int = Field(alias="uncappedWinMinorUnits")


class FeatureCounterUpdatePayload(_FrozenPayload):
    field: str
    before: int
    after: int


class RuntimeLimitHitPayload(_FrozenPayload):
    limit_code: str = Field(alias="limitCode")
    action: str


class RuntimeFaultPayload(_FrozenPayload):
    fault_code: str = Field(alias="faultCode")
    message: str


class RngDrawPayload(_FrozenPayload):
    stream_id: str = Field(alias="streamId")
    draw_index: int = Field(alias="drawIndex")
    value: int


class GuardEvaluatedPayload(_FrozenPayload):
    guard_expression: str = Field(alias="guardExpression")
    result: bool


PAYLOAD_MODEL_BY_EVENT_TYPE: dict[str, type[_FrozenPayload]] = {
    "SPIN_CHAIN_START": SpinChainStartPayload,
    "SPIN_CHAIN_END": SpinChainEndPayload,
    "FRAME_PUSH": FramePushPayload,
    "FRAME_POP": FramePopPayload,
    "STATE_ENTER": StateEnterPayload,
    "STATE_REENTER": StateReenterPayload,
    "GRID_RESULT": GridResultPayload,
    "WIN_EVALUATED": WinEvaluatedPayload,
    "TRIGGER_EMITTED": TriggerEmittedPayload,
    "TRANSITION_TAKEN": TransitionTakenPayload,
    "MULTIPLIER_APPLIED": MultiplierAppliedPayload,
    "EXPOSURE_CAP_APPLIED": ExposureCapAppliedPayload,
    "FEATURE_COUNTER_UPDATE": FeatureCounterUpdatePayload,
    "RUNTIME_LIMIT_HIT": RuntimeLimitHitPayload,
    "RUNTIME_FAULT": RuntimeFaultPayload,
    "RNG_DRAW": RngDrawPayload,
    "GUARD_EVALUATED": GuardEvaluatedPayload,
}


def validate_payload(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and freeze payload for ``event_type``; returns canonical JSON dict."""
    model_cls = PAYLOAD_MODEL_BY_EVENT_TYPE.get(event_type)
    if model_cls is None:
        msg = f"unknown event type for payload validation: {event_type}"
        raise ValueError(msg)
    model = model_cls.model_validate(payload)
    return model.model_dump(mode="json", by_alias=True, exclude_none=True)
