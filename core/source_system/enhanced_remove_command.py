"""
Enhanced remove-source command with advanced features:
- Dry-run mode
- Automatic backups
- Usage analytics
- Batch removal from file
- Undo/restore functionality
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from core.exceptions import CapcatError
from core.logging_config import get_logger
from core.source_system.remove_source_command import (
    RemoveSourceCommand,
    SourceRemovalInfo,
    RemovalUserInterface
)
from core.source_system.source_backup_manager import (
    SourceBackupManager,
    BackupMetadata,
    BackupStrategy
)
from core.source_system.source_analytics import (
    SourceAnalytics,
    SourceUsageStats,
    AnalyticsReporter
)


@dataclass
class RemovalOptions:
    """Options for source removal."""
    dry_run: bool = False
    create_backup: bool = True
    show_analytics: bool = True
    batch_file: Optional[Path] = None
    force: bool = False  # Skip confirmations


class EnhancedRemoveCommand:
    """
    Enhanced removal command with analytics, backups, and dry-run support.
    Extends base RemoveSourceCommand with advanced features.
    """

    def __init__(
        self,
        base_command: RemoveSourceCommand,
        backup_manager: SourceBackupManager,
        analytics: SourceAnalytics,
        ui: RemovalUserInterface,
        logger: Optional[any] = None
    ):
        self._base_command = base_command
        self._backup_manager = backup_manager
        self._analytics = analytics
        self._ui = ui
        self._logger = logger or get_logger(__name__)

    def execute_with_options(self, options: RemovalOptions) -> None:
        """
        Execute removal with enhanced options.

        Args:
            options: RemovalOptions specifying behavior
        """
        try:
            # Handle batch file if provided
            if options.batch_file:
                self._execute_batch_removal(options)
                return

            # Standard interactive removal with enhancements
            self._execute_enhanced_removal(options)

        except CapcatError:
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error: {e}")
            raise CapcatError(f"Unexpected error: {e}") from e

    def execute_undo(self, backup_id: Optional[str] = None) -> None:
        """
        Undo a previous removal by restoring from backup.

        Args:
            backup_id: Specific backup to restore (None = most recent)
        """
        self._logger.info("Starting undo operation")

        # List available backups
        backups = self._backup_manager.list_backups()

        if not backups:
            self._ui.show_info("No backups available to restore.")
            return

        # Let user select backup if not specified
        if backup_id is None:
            backup_id = self._select_backup_to_restore(backups)
            if not backup_id:
                self._ui.show_info("Restore cancelled.")
                return

        # Show what will be restored
        backup = next((b for b in backups if b.backup_id == backup_id), None)
        if not backup:
            raise CapcatError(f"Backup not found: {backup_id}")

        self._ui.show_info(f"\nRestoring backup: {backup.backup_id}")
        self._ui.show_info(f"Timestamp: {backup.timestamp}")
        self._ui.show_info(f"Sources: {', '.join(backup.sources)}")

        # Confirm restore
        from core.source_system.removal_ui import QuestionaryRemovalUI
        if isinstance(self._ui, QuestionaryRemovalUI):
            import questionary
            from prompt_toolkit.styles import Style
            custom_style = Style([('answer', 'fg:#d75f00')])

            confirmed = questionary.confirm(
                "  Proceed with restore?",
                default=False,
                style=custom_style,
                qmark=""
            ).ask()

            if not confirmed:
                self._ui.show_info("Restore cancelled.")
                return

        # Perform restore
        try:
            import cli
            app_root = Path(cli.__file__).parent
            config_path = app_root / "sources" / "active" / "config_driven" / "configs"
            bundles_path = app_root / "sources" / "active" / "bundles.yml"

            restored = self._backup_manager.restore_backup(
                backup_id, config_path, bundles_path
            )

            # Refresh registry
            from core.source_system.source_registry import reset_source_registry
            reset_source_registry()

            self._ui.show_success(
                f"Restored {len(restored)} source(s): {', '.join(restored)}"
            )

        except Exception as e:
            self._logger.error(f"Restore failed: {e}")
            raise CapcatError(f"Failed to restore backup: {e}") from e

    def _execute_enhanced_removal(self, options: RemovalOptions) -> None:
        """Execute standard interactive removal with enhancements."""
        # Get sources using base command's lister
        available_sources = self._base_command._source_lister.get_available_sources()

        if not available_sources:
            self._ui.show_info("No sources available to remove.")
            return

        # Show analytics if requested
        if options.show_analytics:
            self._show_analytics_summary(available_sources)

        # Let user select sources
        selected_ids = self._ui.select_sources_to_remove(available_sources)
        if not selected_ids:
            self._ui.show_info("No sources selected for removal.")
            return

        # Gather source info
        sources_info = []
        for source_id in selected_ids:
            info = self._base_command._source_info_provider.get_source_info(source_id)
            if info:
                sources_info.append(info)

        # Show analytics for selected sources
        if options.show_analytics:
            self._show_selected_analytics(sources_info)

        # Show removal summary
        self._ui.show_removal_summary(sources_info)

        # Scan for output directories
        output_directories = self._scan_output_directories(sources_info)
        cleanup_archives = False

        if output_directories:
            total_size = self._calculate_directory_size(output_directories)
            cleanup_archives = self._prompt_output_cleanup(
                output_directories, total_size, options.dry_run, options.force
            )

        # Dry-run mode - stop here
        if options.dry_run:
            self._ui.show_info("\n[DRY RUN] No changes made.")
            self._show_dry_run_summary(sources_info, output_directories if cleanup_archives else None)
            return

        # Confirm removal
        if not options.force:
            if not self._ui.confirm_removal(sources_info):
                self._ui.show_info("Removal cancelled.")
                return

        # Create backup if requested
        backup_metadata = None
        if options.create_backup:
            backup_metadata = self._create_backup(
                sources_info,
                output_directories if cleanup_archives else None
            )

        # Perform removal
        self._base_command._remove_sources(sources_info)

        # Delete output directories if requested
        deleted_archives = 0
        deleted_size = 0
        if cleanup_archives and output_directories:
            deleted_archives, deleted_size = self._delete_output_directories(output_directories)

        # Refresh registry
        self._base_command._refresh_registry()

        # Show success with backup info
        message = f"Successfully removed {len(sources_info)} source(s)."
        if cleanup_archives and deleted_archives > 0:
            message += f"\nDeleted {deleted_archives} output archive(s) ({self._format_size(deleted_size)})."
        if backup_metadata:
            message += f"\nBackup created: {backup_metadata.backup_id}"
            message += f"\nRestore with: ./capcat remove-source --undo {backup_metadata.backup_id}"

        self._ui.show_success(message)

    def _execute_batch_removal(self, options: RemovalOptions) -> None:
        """Execute batch removal from file."""
        if not options.batch_file.exists():
            raise CapcatError(f"Batch file not found: {options.batch_file}")

        # Read source IDs from file
        try:
            with open(options.batch_file, 'r') as f:
                source_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            raise CapcatError(f"Failed to read batch file: {e}") from e

        if not source_ids:
            self._ui.show_info("No sources listed in batch file.")
            return

        self._ui.show_info(f"Batch removal: {len(source_ids)} sources from {options.batch_file.name}")

        # Gather source info
        sources_info = []
        not_found = []
        for source_id in source_ids:
            info = self._base_command._source_info_provider.get_source_info(source_id)
            if info:
                sources_info.append(info)
            else:
                not_found.append(source_id)

        if not_found:
            self._ui.show_info(f"Sources not found: {', '.join(not_found)}")

        if not sources_info:
            self._ui.show_info("No valid sources to remove.")
            return

        # Show what will be removed
        self._ui.show_removal_summary(sources_info)

        # Dry-run mode
        if options.dry_run:
            self._ui.show_info("\n[DRY RUN] No changes made.")
            return

        # Confirm if not forced
        if not options.force:
            if not self._ui.confirm_removal(sources_info):
                self._ui.show_info("Batch removal cancelled.")
                return

        # Create backup
        backup_metadata = None
        if options.create_backup:
            backup_metadata = self._create_backup(sources_info)

        # Perform removal
        self._base_command._remove_sources(sources_info)
        self._base_command._refresh_registry()

        # Success message
        message = f"Batch removal complete: {len(sources_info)} sources removed."
        if backup_metadata:
            message += f"\nBackup: {backup_metadata.backup_id}"

        self._ui.show_success(message)

    def _create_backup(
        self,
        sources_info: List[SourceRemovalInfo],
        output_directories: Optional[List[Path]] = None
    ) -> BackupMetadata:
        """
        Create backup before removal.

        Args:
            sources_info: List of sources being removed
            output_directories: Optional list of output directories to backup
        """
        try:
            source_ids = [s.source_id for s in sources_info]
            config_paths = [s.config_path for s in sources_info]

            import cli
            app_root = Path(cli.__file__).parent
            bundles_path = app_root / "sources" / "active" / "bundles.yml"

            backup_metadata = self._backup_manager.create_backup(
                source_ids, config_paths, bundles_path
            )

            # Backup output directories if provided
            if output_directories:
                self._backup_output_directories(
                    output_directories, backup_metadata.backup_path
                )

            return backup_metadata

        except Exception as e:
            self._logger.error(f"Backup creation failed: {e}")
            raise CapcatError(f"Failed to create backup: {e}") from e

    def _show_analytics_summary(self, available_sources: List[tuple[str, str]]) -> None:
        """Show analytics summary before removal."""
        self._ui.show_info("\n--- Source Usage Analytics ---")

        source_dict = {sid: name for sid, name in available_sources}
        all_stats = self._analytics.get_all_stats(source_dict)

        # Show top 5 most used
        if all_stats:
            self._ui.show_info("\nMost Active Sources:")
            for stats in all_stats[:5]:
                if stats.total_fetches > 0:
                    self._ui.show_info(
                        f"  {stats.display_name}: {stats.total_fetches} fetches, "
                        f"{stats.fetch_frequency}"
                    )

        # Show unused sources
        unused = self._analytics.get_unused_sources([s[0] for s in available_sources])
        if unused:
            self._ui.show_info(f"\nUnused sources ({len(unused)}): {', '.join(unused)}")

        self._ui.show_info("")

    def _show_selected_analytics(self, sources_info: List[SourceRemovalInfo]) -> None:
        """Show detailed analytics for selected sources."""
        self._ui.show_info("\n--- Selected Sources Analytics ---\n")

        for info in sources_info:
            stats = self._analytics.get_source_stats(info.source_id, info.display_name)
            recommendation = AnalyticsReporter.format_removal_recommendation(stats)

            self._ui.show_info(f"{info.display_name} ({info.source_id})")
            self._ui.show_info(f"  Fetches: {stats.total_fetches}, Frequency: {stats.fetch_frequency}")
            self._ui.show_info(f"  {recommendation}\n")

    def _show_dry_run_summary(
        self,
        sources_info: List[SourceRemovalInfo],
        output_directories: Optional[List[Path]] = None
    ) -> None:
        """Show what would happen in dry-run mode."""
        self._ui.show_info("\nActions that would be performed:")

        for info in sources_info:
            self._ui.show_info(f"\n  {info.display_name} ({info.source_id}):")
            self._ui.show_info(f"    - Delete: {info.config_path}")
            if info.bundles:
                self._ui.show_info(f"    - Remove from bundles: {', '.join(info.bundles)}")

        if output_directories:
            total_size = self._calculate_directory_size(output_directories)
            self._ui.show_info(f"\n  Output archives:")
            self._ui.show_info(f"    - Delete {len(output_directories)} directories ({self._format_size(total_size)})")
            for directory in output_directories[:5]:  # Show first 5
                self._ui.show_info(f"      • {directory.name}")
            if len(output_directories) > 5:
                self._ui.show_info(f"      ... and {len(output_directories) - 5} more")

        self._ui.show_info("\nTo execute, run without --dry-run flag.")

    def _select_backup_to_restore(self, backups: List[BackupMetadata]) -> Optional[str]:
        """Let user select which backup to restore."""
        from core.source_system.removal_ui import QuestionaryRemovalUI

        if not isinstance(self._ui, QuestionaryRemovalUI):
            # Use most recent backup
            return backups[0].backup_id if backups else None

        import questionary
        from prompt_toolkit.styles import Style
        custom_style = Style([
            ('selected', 'fg:#d75f00'),
            ('pointer', 'fg:#d75f00 bold'),
        ])

        choices = [
            questionary.Choice(
                f"{b.backup_id} - {len(b.sources)} sources - {b.timestamp[:19]}",
                b.backup_id
            )
            for b in sorted(backups, key=lambda x: x.timestamp, reverse=True)
        ]

        return questionary.select(
            "  Select backup to restore:",
            choices=choices,
            style=custom_style,
            qmark="",
            pointer=">"
        ).ask()

    def _scan_output_directories(self, sources_info: List[SourceRemovalInfo]) -> List[Path]:
        """
        Scan for output directories matching the sources being removed.

        Searches in ../News/ for directories matching source display names or IDs.

        Args:
            sources_info: List of sources being removed

        Returns:
            List of Path objects for matching output directories
        """
        output_dirs = []

        try:
            import cli
            app_root = Path(cli.__file__).parent
            news_root = app_root.parent / "News"

            if not news_root.exists():
                return []

            # Build patterns to match
            patterns = set()
            for info in sources_info:
                # Pattern 1: Display name with underscores (e.g., "Hacker_News_")
                display_pattern = info.display_name.replace(' ', '_') + '_'
                patterns.add(display_pattern.lower())

                # Pattern 2: Source ID (e.g., "hn_")
                patterns.add(f"{info.source_id}_".lower())

            self._logger.debug(f"Scanning for output directories with patterns: {patterns}")

            # Scan all news_* directories
            news_dirs_found = list(news_root.glob("news_*"))
            self._logger.debug(f"Found {len(news_dirs_found)} news_* directories in {news_root}")

            for news_dir in news_dirs_found:
                if not news_dir.is_dir():
                    continue

                self._logger.debug(f"Scanning news directory: {news_dir}")

                # Check each subdirectory
                subdirs = list(news_dir.iterdir())
                self._logger.debug(f"  Found {len(subdirs)} subdirectories")

                for source_dir in subdirs:
                    if not source_dir.is_dir():
                        self._logger.debug(f"    Skipping non-directory: {source_dir.name}")
                        continue

                    # Check if directory name matches any pattern
                    dir_name_lower = source_dir.name.lower()
                    self._logger.debug(f"    Checking directory: {source_dir.name} (lower: {dir_name_lower})")

                    for pattern in patterns:
                        matches = dir_name_lower.startswith(pattern)
                        self._logger.debug(f"      Pattern '{pattern}' matches: {matches}")
                        if matches:
                            output_dirs.append(source_dir)
                            self._logger.debug(f"      ✓ Added to output_dirs: {source_dir}")
                            break

        except Exception as e:
            self._logger.warning(f"Error scanning output directories: {e}")

        return output_dirs

    def _calculate_directory_size(self, directories: List[Path]) -> int:
        """
        Calculate total size of directories in bytes.

        Args:
            directories: List of directory paths

        Returns:
            Total size in bytes
        """
        total_size = 0

        for directory in directories:
            try:
                for item in directory.rglob('*'):
                    if item.is_file():
                        total_size += item.stat().st_size
            except Exception as e:
                self._logger.debug(f"Error calculating size for {directory}: {e}")

        return total_size

    def _format_size(self, size_bytes: int) -> str:
        """
        Format byte size as human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string (e.g., "2.3 GB", "45.7 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _prompt_output_cleanup(
        self,
        directories: List[Path],
        total_size: int,
        dry_run: bool,
        force: bool
    ) -> bool:
        """
        Prompt user whether to delete output archives.

        Args:
            directories: List of output directories found
            total_size: Total size in bytes
            dry_run: Whether in dry-run mode
            force: Whether to skip prompt

        Returns:
            True if user wants to delete archives
        """
        if not directories:
            return False

        # In force mode, default to yes
        if force:
            return True

        # Show what was found
        self._ui.show_info(f"\n--- Output Archives Found ---")
        self._ui.show_info(
            f"Found {len(directories)} output archive(s) totaling {self._format_size(total_size)}"
        )

        # Show sample directories
        self._ui.show_info("\nSample directories:")
        for directory in directories[:5]:
            self._ui.show_info(f"  • {directory}")
        if len(directories) > 5:
            self._ui.show_info(f"  ... and {len(directories) - 5} more")

        # Prompt user
        from core.source_system.removal_ui import QuestionaryRemovalUI

        if isinstance(self._ui, QuestionaryRemovalUI):
            import questionary
            from prompt_toolkit.styles import Style
            custom_style = Style([('answer', 'fg:#d75f00')])

            result = questionary.confirm(
                "\n  Also delete these output archives?",
                default=True,
                style=custom_style,
                qmark=""
            ).ask()

            return result if result is not None else False

        # Fallback for non-interactive UI
        return True

    def _backup_output_directories(self, directories: List[Path], backup_path: Path) -> None:
        """
        Backup output directories before deletion.

        Args:
            directories: List of directories to backup
            backup_path: Path to backup directory
        """
        import shutil

        archives_backup_path = backup_path / "archives"
        archives_backup_path.mkdir(exist_ok=True)

        self._logger.info(f"Backing up {len(directories)} output directories")

        for directory in directories:
            try:
                # Create backup with same name
                backup_dest = archives_backup_path / directory.name
                shutil.copytree(directory, backup_dest)
                self._logger.debug(f"Backed up: {directory} -> {backup_dest}")
            except Exception as e:
                self._logger.warning(f"Failed to backup {directory}: {e}")

    def _delete_output_directories(self, directories: List[Path]) -> tuple[int, int]:
        """
        Delete output directories.

        Args:
            directories: List of directories to delete

        Returns:
            Tuple of (number_deleted, total_size_deleted)
        """
        import shutil

        deleted_count = 0
        deleted_size = 0

        for directory in directories:
            try:
                # Calculate size before deletion
                dir_size = sum(
                    f.stat().st_size
                    for f in directory.rglob('*')
                    if f.is_file()
                )

                # Delete directory
                shutil.rmtree(directory)
                deleted_count += 1
                deleted_size += dir_size

                self._logger.info(f"Deleted output directory: {directory}")

            except Exception as e:
                self._logger.error(f"Failed to delete {directory}: {e}")
                self._ui.show_error(f"Failed to delete {directory.name}: {e}")

        return deleted_count, deleted_size