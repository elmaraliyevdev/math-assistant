"""Process-wide security guard singletons."""

from __future__ import annotations

from app.config import Settings
from app.security.brute_force import BruteForceGuard
from app.security.rate_limit import RateLimiter

_auth_rate_limiter: RateLimiter | None = None
_brute_force_guard: BruteForceGuard | None = None


def configure_security_guards(settings: Settings) -> None:
    global _auth_rate_limiter, _brute_force_guard
    _auth_rate_limiter = RateLimiter(
        max_requests=settings.rate_limit_auth_per_minute,
        window_seconds=60,
    )
    _brute_force_guard = BruteForceGuard(
        max_attempts=settings.brute_force_max_attempts,
        lockout_minutes=settings.brute_force_lockout_minutes,
    )


def get_auth_rate_limiter() -> RateLimiter:
    if _auth_rate_limiter is None:
        msg = "security guards not configured"
        raise RuntimeError(msg)
    return _auth_rate_limiter


def get_brute_force_guard() -> BruteForceGuard:
    if _brute_force_guard is None:
        msg = "security guards not configured"
        raise RuntimeError(msg)
    return _brute_force_guard
