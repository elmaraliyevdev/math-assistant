"""Engine-related API exceptions."""

from __future__ import annotations


class EngineVersionMismatchError(Exception):
    """Raised when the requested engine version does not match the deployment."""

    def __init__(self, *, requested: str, deployed: str) -> None:
        self.requested = requested
        self.deployed = deployed
        super().__init__(
            f"engine version mismatch: requested {requested!r}, "
            f"deployed {deployed!r}",
        )
