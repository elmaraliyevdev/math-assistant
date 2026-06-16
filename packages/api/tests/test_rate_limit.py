"""Rate limiter unit tests."""

from __future__ import annotations

import pytest

from app.exceptions.domain import RateLimitExceededError
from app.security.rate_limit import RateLimiter


def test_rate_limiter_allows_under_threshold() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.check("key")
    limiter.check("key")


def test_rate_limiter_blocks_over_threshold() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.check("key")
    limiter.check("key")
    with pytest.raises(RateLimitExceededError):
        limiter.check("key")
