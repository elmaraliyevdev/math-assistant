"""Simulation job models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SimulationJob:
    simulation_id: uuid.UUID
