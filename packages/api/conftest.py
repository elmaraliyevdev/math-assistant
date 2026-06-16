"""Pytest top-level configuration.

Pytest no longer supports declaring `pytest_plugins` in a non-top-level conftest,
since it affects the entire test suite.
"""

import sys

sys.dont_write_bytecode = True

pytest_plugins = ["tests.api.conftest"]

