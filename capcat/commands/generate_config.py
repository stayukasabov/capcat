"""Generate-config command - launches the interactive source config generator."""
from __future__ import annotations

import argparse
import sys


def generate_config(args: argparse.Namespace) -> None:
    """Launch the interactive config generator.

    Args:
        args: Namespace with optional output path.
    """
    from capcat.scripts.generate_source_config import main as _generator_main  # noqa: PLC0415

    # Inject --output into sys.argv so the generator's argparse picks it up.
    argv_backup = sys.argv[:]
    sys.argv = [sys.argv[0]]
    if getattr(args, "output", None):
        sys.argv.extend(["--output", str(args.output)])

    try:
        _generator_main()
    finally:
        sys.argv = argv_backup
