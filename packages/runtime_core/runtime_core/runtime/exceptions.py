"""Runtime Core exceptions."""


class RuntimeError(Exception):
    """Base runtime error."""


class RNGError(RuntimeError):
    """RNG usage or configuration error."""
