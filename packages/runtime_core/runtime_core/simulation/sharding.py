"""Deterministic spin-range sharding for Monte Carlo simulation."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_core.runtime.rng.service import derive_shard_seed


@dataclass(frozen=True, slots=True)
class ShardAssignment:
    shard_index: int
    spin_start: int
    spin_count: int
    shard_seed: bytes


def assign_shards(
    total_spins: int,
    shard_count: int,
    *,
    master_seed: bytes,
    simulation_run_id: str,
) -> tuple[ShardAssignment, ...]:
    """Split *total_spins* across *shard_count* contiguous index ranges."""
    if total_spins < 0:
        msg = f"total_spins must be >= 0, got {total_spins}"
        raise ValueError(msg)
    if shard_count < 1:
        msg = f"shard_count must be >= 1, got {shard_count}"
        raise ValueError(msg)
    if total_spins == 0:
        return tuple(
            ShardAssignment(
                shard_index=index,
                spin_start=0,
                spin_count=0,
                shard_seed=derive_shard_seed(master_seed, index, simulation_run_id),
            )
            for index in range(shard_count)
        )

    base = total_spins // shard_count
    remainder = total_spins % shard_count
    assignments: list[ShardAssignment] = []
    start = 0
    for shard_index in range(shard_count):
        count = base + (1 if shard_index < remainder else 0)
        assignments.append(
            ShardAssignment(
                shard_index=shard_index,
                spin_start=start,
                spin_count=count,
                shard_seed=derive_shard_seed(master_seed, shard_index, simulation_run_id),
            ),
        )
        start += count
    return tuple(assignments)
