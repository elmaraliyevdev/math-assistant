"""Simulation execution errors."""

from __future__ import annotations


class SimulationJobCancelledError(Exception):
    """Raised when a simulation job is cancelled during execution."""
