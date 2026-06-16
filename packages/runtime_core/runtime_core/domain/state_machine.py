"""State machine graph domain types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Progression(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    counter_field: str | None = Field(default=None, alias="counterField")
    decrements_on: str | None = Field(default=None, alias="decrementsOn")
    min_value: int | None = Field(default=None, alias="minValue")
    terminates_when: str | None = Field(default=None, alias="terminatesWhen")


class Transition(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    label: str | None = None
    trigger: str
    priority: int = 0
    priority_tier: str | None = Field(default=None, alias="priorityTier")
    guard: dict[str, Any] | None = None
    effect: str
    target_state_id: str | None = Field(default=None, alias="targetStateId")
    target_machine_id: str | None = Field(default=None, alias="targetMachineId")
    actions: list[Any] | None = None


class State(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    label: str | None = None
    plugin_ref_id: str = Field(alias="pluginRefId")
    state_type: str = Field(alias="stateType")
    terminal: bool = False
    rtp_category: str = Field(alias="rtpCategory")
    plugin_config: dict[str, Any] = Field(default_factory=dict, alias="pluginConfig")
    transitions: list[Transition] = Field(default_factory=list)
    progression: Progression | None = None
    deprecated: bool = False


class StateMachine(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    label: str | None = None
    initial_state_id: str = Field(alias="initialStateId")
    states: dict[str, State]
