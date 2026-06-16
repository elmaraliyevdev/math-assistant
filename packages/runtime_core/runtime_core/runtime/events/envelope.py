"""Runtime event envelope models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from runtime_core.runtime.events.types import EVENT_VERSION, EventType


class EventCorrelation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    simulation_run_id: str = Field(alias="simulationRunId")
    spin_chain_index: int = Field(alias="spinChainIndex")
    game_version_content_hash: str = Field(alias="gameVersionContentHash")
    engine_version: str = Field(alias="engineVersion")


class EventContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    stack_depth: int = Field(alias="stackDepth")
    machine_id: str = Field(alias="machineId")
    state_id: str = Field(alias="stateId")
    frame_id: str = Field(alias="frameId")


class RuntimeEvent(BaseModel):
    """Canonical runtime event envelope."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    event_version: str = Field(default=EVENT_VERSION, alias="eventVersion")
    sequence: int
    event_type: EventType = Field(alias="eventType")
    timestamp_us: int | None = Field(default=None, alias="timestampUs")
    correlation: EventCorrelation
    context: EventContext
    payload: dict[str, Any]

    def replay_unit(self) -> dict[str, Any]:
        """Deterministic replay hash unit; excludes ``timestampUs``."""
        return self.model_dump(
            mode="json",
            by_alias=True,
            exclude={"timestamp_us"},
            exclude_none=True,
        )
