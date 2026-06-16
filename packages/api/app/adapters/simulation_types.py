"""Shared simulation adapter types."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.mathematical import MathematicsReport
from runtime_core.simulation import SimulationResult


@dataclass(frozen=True, slots=True)
class SimulationExecutionOutcome:
    engine_result: SimulationResult
    mathematics_report: MathematicsReport
