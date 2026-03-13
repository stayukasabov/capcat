"""Add-source command — interactive RSS source addition."""
from __future__ import annotations


def add_source(url: str) -> None:
    """Interactive command to add a new RSS-based source.

    Args:
        url: RSS feed URL to add as new source.
    """
    import sys
    from capcat.core.source_system.add_source_service import create_add_source_service
    from capcat.core.exceptions import CapcatError

    try:
        service = create_add_source_service()
        service.add_source(url)
    except CapcatError as exc:
        print(f"Error: {exc.user_message}", file=sys.stderr)
        raise SystemExit(1)
    except (KeyboardInterrupt, TypeError):
        print("\nOperation cancelled by user.", file=sys.stderr)
        raise SystemExit(1)
