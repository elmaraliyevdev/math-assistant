"""Brute-force protection for authentication endpoints."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import Lock

from app.exceptions.domain import AccountLockedError


@dataclass
class BruteForceGuard:
    max_attempts: int
    lockout_minutes: int
    _failures: dict[str, list[datetime]] = field(default_factory=lambda: defaultdict(list))
    _lock: Lock = field(default_factory=Lock)

    def _key(self, email: str, ip: str) -> str:
        return f"{email.strip().lower()}:{ip}"

    def check_allowed(self, email: str, ip: str) -> None:
        key = self._key(email, ip)
        now = datetime.now(tz=UTC)
        cutoff = now - timedelta(minutes=self.lockout_minutes)
        with self._lock:
            recent = [event for event in self._failures[key] if event > cutoff]
            self._failures[key] = recent
            if len(recent) >= self.max_attempts:
                raise AccountLockedError(
                    retry_after_seconds=self.lockout_minutes * 60,
                )

    def record_failure(self, email: str, ip: str) -> None:
        key = self._key(email, ip)
        with self._lock:
            self._failures[key].append(datetime.now(tz=UTC))

    def record_success(self, email: str, ip: str) -> None:
        key = self._key(email, ip)
        with self._lock:
            self._failures.pop(key, None)
