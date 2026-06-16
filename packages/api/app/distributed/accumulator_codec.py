"""Partial accumulator serialization for shard persistence."""

from __future__ import annotations

from dataclasses import asdict

from runtime_core.simulation import PartialAccumulator


def partial_accumulator_to_dict(accumulator: PartialAccumulator) -> dict:
    return asdict(accumulator)


def partial_accumulator_from_dict(payload: dict) -> PartialAccumulator:
    return PartialAccumulator(**payload)
