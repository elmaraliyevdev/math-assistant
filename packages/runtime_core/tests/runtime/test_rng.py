"""RNG service and PCG64 tests."""

from __future__ import annotations

import pytest

from runtime_core.runtime.exceptions import RNGError
from runtime_core.runtime.rng.pcg64 import PCG64
from runtime_core.runtime.rng.service import (
    RNGService,
    RNGServiceConfig,
    _seed_to_pcg64_state,
    default_rng_service_config,
)
from runtime_core.runtime.rng.types import RNGAlgorithm, SeedDerivationPolicy


def test_pcg64_deterministic() -> None:
    a = PCG64(12345, 54)
    b = PCG64(12345, 54)
    for _ in range(20):
        assert a.next_uint64() == b.next_uint64()


def test_pcg64_different_seeds() -> None:
    a = PCG64(1, 54)
    b = PCG64(2, 54)
    assert a.next_uint64() != b.next_uint64()


def test_pcg64_zero_seq_coerced() -> None:
    p = PCG64(99, 0)
    assert p.next_uint64() != 0 or p.next_uint64() != 0


def test_new_service_defaults() -> None:
    svc = RNGService(RNGServiceConfig())
    assert svc.config.algorithm == RNGAlgorithm.PCG64
    assert svc.config.policy == SeedDerivationPolicy.V1_HASH_SHARD


def test_default_rng_service_config() -> None:
    cfg = default_rng_service_config()
    assert cfg.algorithm == RNGAlgorithm.PCG64
    assert cfg.policy == SeedDerivationPolicy.V1_HASH_SHARD


def test_new_service_invalid_algorithm() -> None:
    with pytest.raises(RNGError, match="unsupported rng algorithm"):
        RNGService(RNGServiceConfig(algorithm="bad"))


def test_new_service_invalid_policy() -> None:
    with pytest.raises(RNGError, match="unsupported seed derivation policy"):
        RNGService(RNGServiceConfig(policy="legacy"))


def test_chain_seed_derivation_stable() -> None:
    svc = RNGService(None)
    master = b"master-seed-bytes"
    scope_a = svc.new_chain_scope(master, 0, "run-abc", 42)
    scope_b = svc.new_chain_scope(master, 0, "run-abc", 42)
    assert scope_a.chain_seed() == scope_b.chain_seed()


def test_chain_seed_derivation_distinct() -> None:
    svc = RNGService(None)
    master = b"master-seed-bytes"
    base = svc.new_chain_scope(master, 0, "run", 1).chain_seed()
    assert svc.new_chain_scope(master, 1, "run", 1).chain_seed() != base
    assert svc.new_chain_scope(master, 0, "run", 2).chain_seed() != base
    assert svc.new_chain_scope(master, 0, "run-other", 1).chain_seed() != base


def test_step_and_multiplier_streams_independent() -> None:
    svc = RNGService(None)
    frame = svc.new_chain_scope(b"seed", 0, "run", 0).frame_stream("f-0-0")
    step0 = frame.step_rng(0)
    step1 = frame.step_rng(1)
    assert step0.next_uint64() != step1.next_uint64()
    mult_a = frame.multiplier_rng("mult.ref", 0)
    mult_b = frame.multiplier_rng("mult.ref", 1)
    assert mult_a.next_uint64() != mult_b.next_uint64()
    assert mult_a.next_uint64() != step0.next_uint64()


def test_rng_next_int_bounds() -> None:
    svc = RNGService(None)
    scope = svc.new_chain_scope(b"int-bounds", 0, "run", 0)
    rng = scope.frame_stream("frame").step_rng(0)
    n = 17
    for _ in range(5000):
        value = rng.next_int(n)
        assert 0 <= value < n


def test_rng_next_int_one() -> None:
    svc = RNGService(None)
    rng = svc.new_chain_scope(b"one", 0, "run", 0).frame_stream("f").step_rng(0)
    assert rng.next_int(1) == 0
    assert rng.draw_id == 1


def test_rng_next_int_invalid_n() -> None:
    svc = RNGService(None)
    rng = svc.new_chain_scope(b"panic", 0, "run", 0).frame_stream("f").step_rng(0)
    with pytest.raises(RNGError, match="next_int requires n > 0"):
        rng.next_int(0)


def test_rng_draw_id_increments() -> None:
    svc = RNGService(None)
    rng = svc.new_chain_scope(b"draw-id", 0, "run", 0).frame_stream("f").step_rng(0)
    assert rng.draw_id == 0
    rng.next_uint64()
    rng.next_int(5)
    assert rng.draw_id == 2


def test_seed_to_pcg64_state_pads_short_seed() -> None:
    state, seq = _seed_to_pcg64_state(bytes([1, 2, 3]))
    assert state != 0 or seq != 0


def test_seed_to_pcg64_state_zero_seq_uses_default() -> None:
    seed = bytes(16)
    _, seq = _seed_to_pcg64_state(seed)
    assert seq == 54


def test_chain_seed_copy_isolated() -> None:
    svc = RNGService(None)
    scope = svc.new_chain_scope(b"copy", 0, "run", 0)
    seed = bytearray(scope.chain_seed())
    seed[0] ^= 0xFF
    assert bytes(seed) != scope.chain_seed()


def test_new_service_empty_config_defaults() -> None:
    svc = RNGService(RNGServiceConfig(algorithm="", policy=""))
    assert svc.config.algorithm == RNGAlgorithm.PCG64
    assert svc.config.policy == SeedDerivationPolicy.V1_HASH_SHARD


def test_rng_next_int_negative_n() -> None:
    svc = RNGService(None)
    rng = svc.new_chain_scope(b"n", 0, "run", 0).frame_stream("f").step_rng(0)
    with pytest.raises(RNGError, match="next_int requires n > 0"):
        rng.next_int(-1)


def test_rng_next_int_rejection_branch() -> None:
    svc = RNGService(None)
    rng = svc.new_chain_scope(b"reject", 0, "run", 0).frame_stream("f").step_rng(0)
    calls = 0

    def mock_next() -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return (1 << 64) - 1
        return 0

    rng._pcg.next_uint64 = mock_next  # type: ignore[method-assign]
    assert rng.next_int(17) == 0
    assert calls == 2


def test_multiplier_rng_public_api() -> None:
    svc = RNGService(None)
    stream = svc.new_chain_scope(b"s", 0, "run", 0).frame_stream("frame")
    a = stream.multiplier_rng("m1", 0).next_uint64()
    b = stream.multiplier_rng("m1", 1).next_uint64()
    assert a != b
