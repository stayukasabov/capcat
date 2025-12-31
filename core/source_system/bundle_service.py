"""
Service layer for bundle management.
Orchestrates BundleManager, BundleValidator, and BundleUI.
"""

from typing import Optional
from pathlib import Path

from core.source_system.bundle_manager import BundleManager
from core.source_system.bundle_validator import BundleValidator
from core.source_system.bundle_ui import BundleUI
from core.source_system.source_registry import get_source_registry
from core.logging_config import get_logger
from cli import get_available_sources


class BundleService:
    """
    Service for bundle management operations.
    Coordinates validation, UI, and persistence.
    """

    def __init__(
        self,
        bundles_path: Path,
        ui: BundleUI = None,
        logger = None
    ):
        """
        Args:
            bundles_path: Path to bundles.yml
            ui: BundleUI instance (creates if None)
            logger: Logger instance (creates if None)
        """
        self.manager = BundleManager(str(bundles_path))
        self.validator = BundleValidator(
            bundle_manager=self.manager,
            source_registry=get_source_registry()
        )
        self.ui = ui or BundleUI()
        self.logger = logger or get_logger(__name__)

    def execute_create_bundle(self) -> None:
        """Execute bundle creation workflow."""
        self.logger.info("Starting create bundle workflow")

        # Prompt for bundle data
        bundle_data = self.ui.prompt_create_bundle()
        if not bundle_data:
            self.ui.show_info("Bundle creation cancelled")
            return

        # Validate bundle ID
        id_result = self.validator.validate_bundle_id(bundle_data.bundle_id)
        if not id_result.valid:
            for error in id_result.errors:
                self.ui.show_error(error)
            return

        # Check uniqueness
        unique_result = self.validator.validate_bundle_unique(bundle_data.bundle_id)
        if not unique_result.valid:
            for error in unique_result.errors:
                self.ui.show_error(error)
            return

        # Validate description
        desc_result = self.validator.validate_description(bundle_data.description)
        if not desc_result.valid:
            for error in desc_result.errors:
                self.ui.show_error(error)
            return

        # Validate default count
        count_result = self.validator.validate_default_count(bundle_data.default_count)
        if not count_result.valid:
            for error in count_result.errors:
                self.ui.show_error(error)
            return

        # Create bundle
        try:
            self.manager.create_bundle(
                bundle_id=bundle_data.bundle_id,
                description=bundle_data.description,
                default_count=bundle_data.default_count
            )

            self.ui.show_success(
                f"Bundle '{bundle_data.bundle_id}' created successfully"
            )
            self.logger.info(f"Created bundle: {bundle_data.bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to create bundle: {e}")
            self.logger.error(f"Bundle creation failed: {e}")

    def execute_delete_bundle(self) -> None:
        """Execute bundle deletion workflow."""
        self.logger.info("Starting delete bundle workflow")

        # Get bundles list
        bundles = self.manager.list_bundles()
        if not bundles:
            self.ui.show_info("No bundles available to delete")
            return

        # Select bundle
        bundle_id = self.ui.prompt_select_bundle(
            bundles,
            message="  Select bundle to delete:"
        )

        if not bundle_id:
            self.ui.show_info("Bundle deletion cancelled")
            return

        # Check if protected
        protected_result = self.validator.validate_not_protected(bundle_id)
        if not protected_result.valid:
            for error in protected_result.errors:
                self.ui.show_error(error)
            return

        # Get bundle details for confirmation
        bundle_info = self.manager.get_bundle_details(bundle_id)

        # Confirm deletion
        details = [
            f"Bundle: {bundle_id}",
            f"Description: {bundle_info['description']}",
            f"Sources: {bundle_info['total_sources']}"
        ]

        confirmed = self.ui.prompt_confirm(
            f"Delete bundle '{bundle_id}'?",
            details=details,
            default=False
        )

        if not confirmed:
            self.ui.show_info("Bundle deletion cancelled")
            return

        # Delete bundle
        try:
            self.manager.delete_bundle(bundle_id)
            self.ui.show_success(f"Bundle '{bundle_id}' deleted successfully")
            self.logger.info(f"Deleted bundle: {bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to delete bundle: {e}")
            self.logger.error(f"Bundle deletion failed: {e}")

    def execute_edit_bundle(self) -> None:
        """Execute bundle editing workflow."""
        self.logger.info("Starting edit bundle workflow")

        # Get bundles list
        bundles = self.manager.list_bundles()
        if not bundles:
            self.ui.show_info("No bundles available to edit")
            return

        # Select bundle
        bundle_id = self.ui.prompt_select_bundle(
            bundles,
            message="  Select bundle to edit:"
        )

        if not bundle_id:
            self.ui.show_info("Bundle editing cancelled")
            return

        # Check if protected
        protected_result = self.validator.validate_not_protected(bundle_id)
        if not protected_result.valid:
            for error in protected_result.errors:
                self.ui.show_error(error)
            return

        # Get current metadata
        bundle_info = self.manager.get_bundle_details(bundle_id)

        # Prompt for new values
        updates = self.ui.prompt_edit_bundle_metadata(
            bundle_info['description'],
            bundle_info['default_count']
        )

        if not updates:
            self.ui.show_info("Bundle editing cancelled")
            return

        # Check if anything changed
        if updates['description'] is None and updates['default_count'] is None:
            self.ui.show_info("No changes made")
            return

        # Validate new values if provided
        if updates['description']:
            desc_result = self.validator.validate_description(updates['description'])
            if not desc_result.valid:
                for error in desc_result.errors:
                    self.ui.show_error(error)
                return

        if updates['default_count']:
            count_result = self.validator.validate_default_count(updates['default_count'])
            if not count_result.valid:
                for error in count_result.errors:
                    self.ui.show_error(error)
                return

        # Update bundle
        try:
            self.manager.update_bundle_metadata(
                bundle_id=bundle_id,
                description=updates['description'],
                default_count=updates['default_count']
            )

            self.ui.show_success(f"Bundle '{bundle_id}' updated successfully")
            self.logger.info(f"Updated bundle: {bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to update bundle: {e}")
            self.logger.error(f"Bundle update failed: {e}")

    def execute_add_sources(self) -> None:
        """Execute add sources to bundle workflow."""
        self.logger.info("Starting add sources workflow")

        # Get bundles list
        bundles = self.manager.list_bundles()
        if not bundles:
            self.ui.show_info("No bundles available")
            return

        # Select bundle
        bundle_id = self.ui.prompt_select_bundle(
            bundles,
            message="  Select bundle to add sources to:"
        )

        if not bundle_id:
            self.ui.show_info("Operation cancelled")
            return

        # Get bundle details
        bundle_info = self.manager.get_bundle_details(bundle_id)

        # Get available sources (exclude those already in bundle)
        all_sources = get_available_sources()
        available_sources = {
            sid: name for sid, name in all_sources.items()
            if sid not in bundle_info['sources']
        }

        if not available_sources:
            self.ui.show_info(f"All sources already in bundle '{bundle_id}'")
            return

        # Select sources to add
        selected_sources = self.ui.prompt_select_sources(
            available_sources,
            message=f"  Select sources to add to '{bundle_id}':"
        )

        if not selected_sources:
            self.ui.show_info("No sources selected")
            return

        # Add sources
        try:
            added_count = self.manager.add_sources_to_bundle(bundle_id, selected_sources)
            self.ui.show_success(
                f"Added {added_count} source(s) to bundle '{bundle_id}'"
            )
            self.logger.info(f"Added {added_count} sources to bundle: {bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to add sources: {e}")
            self.logger.error(f"Add sources failed: {e}")

    def execute_remove_sources(self) -> None:
        """Execute remove sources from bundle workflow."""
        self.logger.info("Starting remove sources workflow")

        # Get bundles list
        bundles = self.manager.list_bundles()
        if not bundles:
            self.ui.show_info("No bundles available")
            return

        # Select bundle
        bundle_id = self.ui.prompt_select_bundle(
            bundles,
            message="  Select bundle to remove sources from:"
        )

        if not bundle_id:
            self.ui.show_info("Operation cancelled")
            return

        # Get bundle details
        bundle_info = self.manager.get_bundle_details(bundle_id)

        if not bundle_info['sources']:
            self.ui.show_info(f"Bundle '{bundle_id}' has no sources")
            return

        # Get sources in bundle
        all_sources = get_available_sources()
        bundle_sources = {
            sid: all_sources.get(sid, sid) for sid in bundle_info['sources']
        }

        # Select sources to remove
        selected_sources = self.ui.prompt_select_sources(
            bundle_sources,
            message=f"  Select sources to remove from '{bundle_id}':",
            group_by_category=False
        )

        if not selected_sources:
            self.ui.show_info("No sources selected")
            return

        # Remove sources
        try:
            removed_count = self.manager.remove_sources_from_bundle(bundle_id, selected_sources)
            self.ui.show_success(
                f"Removed {removed_count} source(s) from bundle '{bundle_id}'"
            )
            self.logger.info(f"Removed {removed_count} sources from bundle: {bundle_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to remove sources: {e}")
            self.logger.error(f"Remove sources failed: {e}")

    def execute_move_source(self) -> None:
        """Execute move source between bundles workflow."""
        self.logger.info("Starting move source workflow")

        # Get all sources
        all_sources = get_available_sources()

        # Select source(s) to move
        selected_sources = self.ui.prompt_select_sources(
            all_sources,
            message="  Select source(s) to move/copy:"
        )

        if not selected_sources:
            self.ui.show_info("No sources selected")
            return

        # For simplicity, handle single source for now
        # TODO: Implement multi-source move
        source_id = selected_sources[0]

        # Get bundles containing this source
        memberships = self.manager.get_source_bundle_memberships(source_id)

        if not memberships:
            self.ui.show_info(f"Source '{source_id}' is not in any bundle")
            return

        # Select source bundle
        source_bundles = [
            {'bundle_id': bid, 'source_count': 0, 'description': '', 'default_count': 0}
            for bid in memberships
        ]

        from_bundle = self.ui.prompt_select_bundle(
            source_bundles,
            message="  Select source bundle:"
        )

        if not from_bundle:
            self.ui.show_info("Operation cancelled")
            return

        # Select copy or move mode
        mode = self.ui.prompt_copy_or_move()
        if not mode or mode == "cancel":
            self.ui.show_info("Operation cancelled")
            return

        copy_mode = (mode == "copy")

        # Get all bundles for target
        all_bundles = self.manager.list_bundles()
        target_bundles = [b for b in all_bundles if b['bundle_id'] != from_bundle]

        # Select target bundle
        to_bundle = self.ui.prompt_select_bundle(
            target_bundles,
            message="  Select target bundle:"
        )

        if not to_bundle:
            self.ui.show_info("Operation cancelled")
            return

        # Move/copy source
        try:
            result = self.manager.move_source_between_bundles(
                source_id,
                from_bundle,
                to_bundle,
                copy_mode=copy_mode
            )

            action = "Copied" if copy_mode else "Moved"
            self.ui.show_success(
                f"{action} '{source_id}' from '{from_bundle}' to '{to_bundle}'"
            )
            self.logger.info(f"{action} source: {source_id}")

        except Exception as e:
            self.ui.show_error(f"Failed to move source: {e}")
            self.logger.error(f"Move source failed: {e}")

    def execute_list_bundles(self) -> None:
        """Execute list bundles workflow."""
        self.logger.info("Listing all bundles")

        bundles = self.manager.list_bundles()
        self.ui.show_all_bundles(bundles)
