"""Deterministic RNG service with HMAC-SHA256 seed derivation."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from runtime_core.runtime.exceptions import RNGError
from runtime_core.runtime.rng.pcg64 import PCG64
from runtime_core.runtime.rng.types import RNGAlgorithm, SeedDerivationPolicy


@dataclass(frozen=True, slots=True)
class RNGServiceConfig:
    algorithm: str = RNGAlgorithm.PCG64
    policy: str = SeedDerivationPolicy.V1_HASH_SHARD


def default_rng_service_config() -> RNGServiceConfig:
    return RNGServiceConfig()


class _DrawRNG:
    __slots__ = ("_pcg", "_draw_id")

    def __init__(self, seed: bytes) -> None:
        state, seq = _seed_to_pcg64_state(seed)
        self._pcg = PCG64(state, seq)
        self._draw_id = 0

    def next_uint64(self) -> int:
        self._draw_id += 1
        return self._pcg.next_uint64()

    def next_int(self, n: int) -> int:
        if n <= 0:
            msg = f"rng: next_int requires n > 0, got {n}"
            raise RNGError(msg)
        if n == 1:
            self._draw_id += 1
            return 0
        limit = ((1 << 64) // n) * n
        while True:
            value = self._pcg.next_uint64()
            if value < limit:
                self._draw_id += 1
                return int(value % n)

    @property
    def draw_id(self) -> int:
        return self._draw_id


@dataclass(frozen=True, slots=True)
class ChainScope:
    _chain_seed: bytes

    def chain_seed(self) -> bytes:
        return bytes(self._chain_seed)

    def frame_stream(self, frame_id: str) -> FrameStream:
        seed = _derive_seed(self._chain_seed, frame_id.encode("utf-8"))
        return FrameStream(_frame_stream_seed=seed)


@dataclass(frozen=True, slots=True)
class FrameStream:
    _frame_stream_seed: bytes

    def step_rng(self, step_index: int) -> _DrawRNG:
        label = b"step:" + _encode_int(step_index)
        return _DrawRNG(_derive_seed(self._frame_stream_seed, label))

    def multiplier_rng(self, multiplier_ref_id: str, apply_index: int) -> _DrawRNG:
        label = b"mult:" + multiplier_ref_id.encode("utf-8") + b":" + _encode_int(
            apply_index,
        )
        return _DrawRNG(_derive_seed(self._frame_stream_seed, label))


class RNGService:
    """Derives scoped deterministic RNG streams for spin chains."""

    def __init__(self, config: RNGServiceConfig | None = None) -> None:
        cfg = config or default_rng_service_config()
        algorithm = cfg.algorithm or RNGAlgorithm.PCG64
        policy = cfg.policy or SeedDerivationPolicy.V1_HASH_SHARD
        if algorithm != RNGAlgorithm.PCG64:
            msg = f"unsupported rng algorithm {algorithm!r}"
            raise RNGError(msg)
        if policy != SeedDerivationPolicy.V1_HASH_SHARD:
            msg = f"unsupported seed derivation policy {policy!r}"
            raise RNGError(msg)
        self._config = RNGServiceConfig(algorithm=algorithm, policy=policy)

    @property
    def config(self) -> RNGServiceConfig:
        return self._config

    def new_chain_scope(
        self,
        master_seed: bytes,
        shard_index: int,
        simulation_run_id: str,
        spin_chain_index: int,
    ) -> ChainScope:
        shard_seed = _derive_seed(
            master_seed,
            _encode_int(shard_index),
            simulation_run_id.encode("utf-8"),
        )
        chain_seed = _derive_seed(shard_seed, _encode_int64(spin_chain_index))
        return ChainScope(_chain_seed=chain_seed)


def derive_shard_seed(
    master_seed: bytes,
    shard_index: int,
    simulation_run_id: str,
) -> bytes:
    """ADR-002 v1-hash-shard: HMAC(masterSeed, shardIndex, runId)."""
    return _derive_seed(
        master_seed,
        _encode_int(shard_index),
        simulation_run_id.encode("utf-8"),
    )


def _derive_seed(key: bytes, *parts: bytes) -> bytes:
    mac = hmac.new(key, digestmod=hashlib.sha256)
    for part in parts:
        mac.update(part)
    return mac.digest()


def _encode_int(value: int) -> bytes:
    return value.to_bytes(8, byteorder="big", signed=False)


def _encode_int64(value: int) -> bytes:
    return value.to_bytes(8, byteorder="big", signed=False)


def _seed_to_pcg64_state(seed: bytes) -> tuple[int, int]:
    if len(seed) < 16:
        seed = seed.ljust(16, b"\x00")
    state = int.from_bytes(seed[:8], byteorder="big", signed=False)
    seq = int.from_bytes(seed[8:16], byteorder="big", signed=False)
    if seq == 0:
        seq = 54
    return state, seq
