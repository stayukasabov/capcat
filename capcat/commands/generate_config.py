"""Generate-config command — launches the interactive source config generator."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def generate_config(args: argparse.Namespace) -> None:
    """Launch the interactive config generator script.

    Args:
        args: Namespace with optional output path.
    """
    script_path = (
        Path(__file__).parent.parent.parent / "scripts" / "generate_source_config.py"
    )

    if not script_path.exists():
        print(
            f"Error: Config generator script not found at {script_path}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    cmd = [sys.executable, str(script_path)]
    if getattr(args, "output", None):
        cmd.extend(["--output", args.output])

    result = subprocess.run(cmd, check=False)
    raise SystemExit(result.returncode)
