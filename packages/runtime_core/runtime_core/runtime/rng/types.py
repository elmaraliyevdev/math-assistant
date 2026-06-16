"""RNG configuration types."""

from enum import StrEnum


class RNGAlgorithm(StrEnum):
    PCG64 = "PCG64"


class SeedDerivationPolicy(StrEnum):
    V1_HASH_SHARD = "v1-hash-shard"
