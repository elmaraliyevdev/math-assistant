"""Shard sizing helpers for simulation profiles."""


def compute_shard_count(
    spin_count: int,
    *,
    min_shards: int = 4,
    max_shards: int = 64,
    spins_per_shard: int = 1_000,
) -> int:
    if spin_count <= 0:
        return 1
    target = max(min_shards, (spin_count + spins_per_shard - 1) // spins_per_shard)
    return min(target, max_shards, spin_count)
