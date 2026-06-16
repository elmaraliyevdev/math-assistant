"""Simulation Engine — Monte Carlo orchestration and sharding."""

from runtime_core.simulation.aggregator import AccumulatorAggregator, PartialAccumulator
from runtime_core.simulation.models import SimulationProfile, SimulationResult
from runtime_core.simulation.runner import SimulationRunner, run_simulation
from runtime_core.runtime.rng.service import derive_shard_seed
from runtime_core.simulation.sharding import ShardAssignment, assign_shards

__all__ = [
    "AccumulatorAggregator",
    "PartialAccumulator",
    "ShardAssignment",
    "SimulationProfile",
    "SimulationResult",
    "SimulationRunner",
    "assign_shards",
    "derive_shard_seed",
    "run_simulation",
]
