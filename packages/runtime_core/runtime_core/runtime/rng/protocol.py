"""Plugin-facing RNG protocol."""

from typing import Protocol


class RNG(Protocol):
    """Deterministic draw interface for built-in plugins."""

    def next_uint64(self) -> int:
        """Return next unsigned 64-bit value."""

    def next_int(self, n: int) -> int:
        """Return uniform integer in ``[0, n)``."""

    @property
    def draw_id(self) -> int:
        """Monotonic draw counter for diagnostics and replay."""
