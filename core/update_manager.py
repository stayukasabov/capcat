#!/usr/bin/env python3
"""
Update Manager for Capcat.
Handles the --update flag logic for checking existing content and prompting users.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.logging_config import get_logger
from core.utils import sanitize_filename


class UpdateManager:
    """
    Manages update operations for Capcat.

    Handles:
    - Date checking for existing content
    - User prompts for missing articles/bundles
    - Update logic without deleting old content
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.today = datetime.now().strftime("%d-%m-%Y")

        # Base paths
        application_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.project_root = os.path.dirname(application_dir)
        self.news_dir = os.path.join(self.project_root, "News")
        self.capcats_dir = os.path.join(self.project_root, "Capcats")

    def check_and_handle_update(
        self,
        command_type: str,
        sources: List[str] = None,
        bundle_name: str = None,
        url: str = None,
    ) -> bool:
        """
        Main update handler. Returns True if update should proceed, False if cancelled.

        Args:
            command_type: 'single', 'fetch', or 'bundle'
            sources: List of source names for fetch command
            bundle_name: Bundle name for bundle command
            url: URL for single command

        Returns:
            bool: True if update should proceed, False if cancelled
        """
        try:
            self.logger.info(
                f"UPDATE MODE: Checking {command_type} for updates..."
            )
            self.logger.debug(
                f"Update parameters: sources={sources}, bundle={bundle_name}, url={url}"
            )

            if command_type == "single":
                return self._handle_single_update(url)
            elif command_type == "fetch":
                return self._handle_fetch_update(sources)
            elif command_type == "bundle":
                return self._handle_bundle_update(bundle_name)
            else:
                self.logger.error(f"Unknown command type: {command_type}")
                return False

        except Exception as e:
            self.logger.error(f"Error in update handler: {e}")
            return False

    def _handle_single_update(self, url: str) -> bool:
        """Handle update for single article command."""
        if not url:
            self.logger.error("No URL provided for single article update")
            return False

        # Determine expected article path
        try:
            from core.source_system.base_source import detect_source_from_url

            source = detect_source_from_url(url)
        except ImportError:
            # Fallback to legacy detection
            source = None

        if source:
            # Known source - check in Capcats
            source_folder_name = f"{source.title()}_{self.today}"
            expected_path = os.path.join(
                self.capcats_dir, source_folder_name
            )
        else:
            # Unknown source - check generic pattern
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            url_path = parsed_url.path.rstrip("/")
            url_title = (
                url_path.split("/")[-1] if url_path else parsed_url.netloc
            )
            safe_title = sanitize_filename(url_title, max_length=50)
            cc_folder_name = f"cc_{self.today}-{safe_title}"
            expected_path = os.path.join(self.capcats_dir, cc_folder_name)

        # Check if article exists
        if os.path.exists(expected_path):
            self.logger.info(f"Article already exists at: {expected_path}")
            return self._prompt_update_existing_article(expected_path, url)
        else:
            # Article doesn't exist - prompt to download
            return self._prompt_download_missing_article(url)

    def _handle_fetch_update(self, sources: List[str]) -> bool:
        """Handle update for fetch command."""
        if not sources:
            self.logger.error("No sources provided for fetch update")
            return False

        today_news_dir = os.path.join(self.news_dir, f"news_{self.today}")

        # Check if today's news directory exists
        if not os.path.exists(today_news_dir):
            return self._prompt_start_todays_batch("fetch", sources)

        # Check which sources exist for today
        existing_sources = []
        missing_sources = []

        for source in sources:
            # Get the actual folder name used by the system
            source_folder_name = self._get_source_folder_name(source)
            source_path = os.path.join(today_news_dir, source_folder_name)

            if os.path.exists(source_path):
                existing_sources.append((source, source_path))
            else:
                missing_sources.append(source)

        # Handle the update logic
        if existing_sources and missing_sources:
            # Some exist, some don't
            return self._prompt_mixed_source_update(
                existing_sources, missing_sources
            )
        elif existing_sources and not missing_sources:
            # All exist
            return self._prompt_update_all_existing_sources(existing_sources)
        else:
            # None exist
            return self._prompt_download_missing_sources(sources)

    def _handle_bundle_update(self, bundle_name: str) -> bool:
        """Handle update for bundle command."""
        if not bundle_name:
            self.logger.error("No bundle name provided for bundle update")
            return False

        today_news_dir = os.path.join(self.news_dir, f"news_{self.today}")

        # Check if today's news directory exists
        if not os.path.exists(today_news_dir):
            return self._prompt_start_todays_batch("bundle", [bundle_name])

        # Get bundle sources
        from cli import get_available_bundles

        bundles = get_available_bundles()

        if bundle_name not in bundles:
            self.logger.error(f"Unknown bundle: {bundle_name}")
            return False

        bundle_sources = bundles[bundle_name]

        # Check which sources exist for today
        existing_sources = []
        missing_sources = []

        for source in bundle_sources:
            # Get the actual folder name used by the system
            source_folder_name = self._get_source_folder_name(source)
            source_path = os.path.join(today_news_dir, source_folder_name)

            if os.path.exists(source_path):
                existing_sources.append((source, source_path))
            else:
                missing_sources.append(source)

        # Handle the update logic
        if existing_sources and missing_sources:
            # Some exist, some don't
            return self._prompt_mixed_bundle_update(
                bundle_name, existing_sources, missing_sources
            )
        elif existing_sources and not missing_sources:
            # All exist
            return self._prompt_update_existing_bundle(
                bundle_name, existing_sources
            )
        else:
            # None exist
            return self._prompt_download_missing_bundle(
                bundle_name, bundle_sources
            )

    def _prompt_update_existing_article(
        self, article_path: str, url: str
    ) -> bool:
        """Prompt user for updating an existing article."""
        try:
            response = (
                input(
                    f"\nArticle already exists at: {os.path.basename(article_path)}\n"
                    f"Do you want to update it with latest content? (Yes/No): "
                )
                .strip()
                .lower()
            )

            if response in ["y", "yes"]:
                self.logger.info("User chose to update existing article")
                return True
            else:
                self.logger.info("User chose not to update article")
                return False

        except KeyboardInterrupt:
            self.logger.info("\nOperation cancelled by user")
            return False

    def _prompt_download_missing_article(self, url: str) -> bool:
        """Prompt user to download a missing article."""
        try:
            response = (
                input(
                    f"\nYou don't have this article downloaded yet.\n"
                    f"Do you want to download it? (Yes/No): "
                )
                .strip()
                .lower()
            )

            if response in ["y", "yes"]:
                self.logger.info("User chose to download missing article")
                return True
            else:
                self.logger.info("User chose not to download article")
                return False

        except KeyboardInterrupt:
            self.logger.info("\nOperation cancelled by user")
            return False

    def _prompt_start_todays_batch(
        self, command_type: str, sources_or_bundles: List[str]
    ) -> bool:
        """Prompt user to start today's batch since none exists."""
        try:
            if command_type == "bundle":
                bundle_name = sources_or_bundles[0]
                response = (
                    input(
                        f"\nYou don't have the '{bundle_name}' bundle executed today.\n"
                        f"Would you like to start it? (Yes/No): "
                    )
                    .strip()
                    .lower()
                )
            else:
                sources_str = ", ".join(sources_or_bundles)
                response = (
                    input(
                        f"\nYou don't have any content from sources '{sources_str}' for today.\n"
                        f"Would you like to start fetching? (Yes/No): "
                    )
                    .strip()
                    .lower()
                )

            if response in ["y", "yes"]:
                self.logger.info("User chose to start today's batch")
                return True
            else:
                self.logger.info("User chose not to start batch")
                return False

        except KeyboardInterrupt:
            self.logger.info("\nOperation cancelled by user")
            return False

    def _prompt_mixed_source_update(
        self,
        existing_sources: List[Tuple[str, str]],
        missing_sources: List[str],
    ) -> bool:
        """Prompt when some sources exist and some don't."""
        try:
            existing_names = [source for source, _ in existing_sources]
            existing_str = ", ".join(existing_names)
            missing_str = ", ".join(missing_sources)

            print(f"\nUpdate Status:")
            print(f"✅ Existing: {existing_str}")
            print(f"❌ Missing: {missing_str}")

            response = (
                input(
                    f"\nDo you want to update existing sources and download missing ones? (Yes/No): "
                )
                .strip()
                .lower()
            )

            if response in ["y", "yes"]:
                self.logger.info(
                    "User chose to update existing and download missing sources"
                )
                return True
            else:
                self.logger.info("User chose not to proceed with mixed update")
                return False

        except KeyboardInterrupt:
            self.logger.info("\nOperation cancelled by user")
            return False

    def _prompt_update_all_existing_sources(
        self, existing_sources: List[Tuple[str, str]]
    ) -> bool:
        """Prompt when all sources exist."""
        existing_names = [source for source, _ in existing_sources]
        existing_str = ", ".join(existing_names)

        self.logger.info(f"UPDATE MODE: Getting the latest articles from the targeted source ({existing_str})")
        return True

    def _prompt_download_missing_sources(self, sources: List[str]) -> bool:
        """Auto-download missing sources in update mode."""
        sources_str = ", ".join(sources)
        self.logger.info(f"UPDATE MODE: Getting the latest articles from the targeted source ({sources_str})")
        return True

    def _prompt_mixed_bundle_update(
        self,
        bundle_name: str,
        existing_sources: List[Tuple[str, str]],
        missing_sources: List[str],
    ) -> bool:
        """Prompt when some bundle sources exist and some don't."""
        try:
            existing_names = [source for source, _ in existing_sources]
            existing_str = ", ".join(existing_names)
            missing_str = ", ".join(missing_sources)

            print(f"\nBundle '{bundle_name}' Status:")
            print(f"✅ Existing: {existing_str}")
            print(f"❌ Missing: {missing_str}")

            response = (
                input(
                    f"\nDo you want to update existing and download missing sources? (Yes/No): "
                )
                .strip()
                .lower()
            )

            if response in ["y", "yes"]:
                self.logger.info(
                    f"User chose to update bundle '{bundle_name}' (mixed)"
                )
                return True
            else:
                self.logger.info(
                    "User chose not to proceed with bundle update"
                )
                return False

        except KeyboardInterrupt:
            self.logger.info("\nOperation cancelled by user")
            return False

    def _prompt_update_existing_bundle(
        self, bundle_name: str, existing_sources: List[Tuple[str, str]]
    ) -> bool:
        """Prompt when entire bundle exists."""
        existing_names = [source for source, _ in existing_sources]
        existing_str = ", ".join(existing_names)

        self.logger.info(f"UPDATE MODE: Getting the latest articles from the targeted source ({existing_str})")
        return True

    def _prompt_download_missing_bundle(
        self, bundle_name: str, bundle_sources: List[str]
    ) -> bool:
        """Prompt when no bundle sources exist."""
        sources_str = ", ".join(bundle_sources)
        self.logger.info(f"UPDATE MODE: Getting the latest articles from the targeted source ({sources_str})")
        return True

    def _get_source_folder_name(self, source: str) -> str:
        """Get the actual folder name used by the system for a source."""
        from core.utils import get_source_folder_name
        base_name = get_source_folder_name(source)
        return f"{base_name} {self.today}"


def get_update_manager() -> UpdateManager:
    """Get a singleton instance of UpdateManager."""
    if not hasattr(get_update_manager, "_instance"):
        get_update_manager._instance = UpdateManager()
    return get_update_manager._instance
