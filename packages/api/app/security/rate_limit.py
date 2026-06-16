"""In-memory sliding-window rate limiter for auth endpoints."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import Lock

from app.exceptions.domain import RateLimitExceededError


def client_ip(forwarded_for: str | None, remote_addr: str | None) -> str:
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return remote_addr or "unknown"


@dataclass
class RateLimiter:
    max_requests: int
    window_seconds: int
    _events: dict[str, list[datetime]] = field(default_factory=lambda: defaultdict(list))
    _lock: Lock = field(default_factory=Lock)

    def check(self, key: str) -> None:
        now = datetime.now(tz=UTC)
        cutoff = now - timedelta(seconds=self.window_seconds)
        with self._lock:
            recent = [event for event in self._events[key] if event > cutoff]
            if len(recent) >= self.max_requests:
                raise RateLimitExceededError()
            recent.append(now)
            self._events[key] = recent
