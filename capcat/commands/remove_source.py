"""Remove-source command — interactive source removal with backup/undo support."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def remove_source(args: argparse.Namespace) -> None:
    """Enhanced command to remove existing sources.

    Args:
        args: Namespace with dry_run, no_backup, no_analytics, force, batch, undo.
    """
    from capcat.core.exceptions import CapcatError
    from capcat.core.logging_config import get_logger
    from capcat.core.source_system.enhanced_remove_command import (
        EnhancedRemoveCommand,
        RemovalOptions,
    )
    from capcat.core.source_system.source_backup_manager import SourceBackupManager
    from capcat.core.source_system.source_analytics import SourceAnalytics
    from capcat.core.source_system.removal_ui import QuestionaryRemovalUI
    from capcat.core.source_system.remove_source_service import (
        create_remove_source_service,
    )

    undo = getattr(args, "undo", None)

    try:
        service = create_remove_source_service()
        base_command = service._create_remove_source_command()
        enhanced_command = EnhancedRemoveCommand(
            base_command=base_command,
            backup_manager=SourceBackupManager(),
            analytics=SourceAnalytics(),
            ui=QuestionaryRemovalUI(),
            logger=get_logger(__name__),
        )

        if undo is not None:
            backup_id = None if undo == "latest" else undo
            enhanced_command.execute_undo(backup_id)
            return

        options = RemovalOptions(
            dry_run=getattr(args, "dry_run", False),
            create_backup=not getattr(args, "no_backup", False),
            show_analytics=not getattr(args, "no_analytics", False),
            batch_file=(Path(args.batch) if getattr(args, "batch", None) else None),
            force=getattr(args, "force", False),
        )
        enhanced_command.execute_with_options(options)

    except CapcatError as exc:
        print(f"Error: {exc.user_message}", file=sys.stderr)
        raise SystemExit(1)
    except (KeyboardInterrupt, TypeError):
        print("\nOperation cancelled by user.", file=sys.stderr)
        raise SystemExit(1)
