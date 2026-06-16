"""Distribution classifier edge coverage."""

from __future__ import annotations

from runtime_core.mathematical.distribution import _classify_multiplier, default_bucket_specs


def test_classify_multiplier_intermediate_buckets() -> None:
    specs = default_bucket_specs()
    assert _classify_multiplier(25.0, specs) == "10-50x"
    assert _classify_multiplier(75.0, specs) == "50-100x"
    assert _classify_multiplier(250.0, specs) == "100-500x"
