"""capcat init command — implementation in Task 4."""
from __future__ import annotations
from pathlib import Path


class AlreadyInitializedError(Exception):
    """Raised when init is called on an existing project without --reinit."""


def init_project(root: Path, reinit: bool = False) -> None:
    """Placeholder — full implementation in Task 4."""
    raise NotImplementedError(
        "capcat init not yet implemented. Coming in Task 4."
    )
