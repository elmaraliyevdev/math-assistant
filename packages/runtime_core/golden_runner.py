#!/usr/bin/env python3
"""Golden runtime validation runner (Phase M7).

Usage:
    golden-runner --all
    golden-runner --fixture fixture-01-base-5x3
    golden-runner --all --determinism
"""

from runtime_core.golden.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
