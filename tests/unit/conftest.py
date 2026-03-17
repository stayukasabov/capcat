"""Unit-test configuration.

Stubs heavyweight optional dependencies into sys.modules *before* any test
module is collected, so module-level imports that reference these packages
do not raise ImportError.
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock


def pytest_configure(config):
    """Pre-stub modules that are not installed in the unit-test environment."""
    for name in ("yt_dlp",):
        if name not in sys.modules:
            sys.modules[name] = MagicMock()
