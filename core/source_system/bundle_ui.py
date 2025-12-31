"""
User interface components for bundle management.
Uses questionary for consistent menu design.
"""

import questionary
from typing import List, Dict, Optional
from prompt_toolkit.styles import Style

from core.source_system.bundle_models import BundleData


# Consistent orange theme
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),
    ('question', 'bold'),
    ('selected', 'fg:#d75f00'),
    ('pointer', 'fg:#d75f00 bold'),
    ('answer', 'fg:#d75f00'),
])


class BundleUI:
    """Interactive UI for bundle management."""

    def __init__(self):
        self.style = custom_style

    def show_bundle_menu(self) -> Optional[str]:
        """
        Show main bundle management menu.

        Returns:
            Selected action or None if cancelled
        """
        choices = [
            questionary.Choice("Create New Bundle", "create"),
            questionary.Choice("Edit Bundle Metadata", "edit"),
            questionary.Choice("Delete Bundle", "delete"),
            questionary.Separator(),
            questionary.Choice("Add Sources to Bundle", "add_sources"),
            questionary.Choice("Remove Sources from Bundle", "remove_sources"),
            questionary.Choice("Move Sources Between Bundles", "move_sources"),
            questionary.Separator(),
            questionary.Choice("View All Bundles", "list"),
            questionary.Separator("─" * 50),
            questionary.Choice("Back to Source Management", "back"),
        ]

        return questionary.select(
            "  Bundle Management - Select an option:",
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    def prompt_create_bundle(self) -> Optional[BundleData]:
        """
        Prompt user for new bundle information.

        Returns:
            BundleData or None if cancelled
        """
        print("\n--- Create New Bundle ---")

        # Bundle ID
        bundle_id = questionary.text(
            "  Bundle ID (lowercase_with_underscores):",
            style=self.style,
            qmark="",
        ).ask()

        if not bundle_id:
            return None

        # Description
        description = questionary.text(
            "  Description:",
            style=self.style,
            qmark="",
        ).ask()

        if not description:
            return None

        # Default count
        default_count_str = questionary.text(
            "  Default article count (default: 20):",
            default="20",
            style=self.style,
            qmark="",
        ).ask()

        if not default_count_str:
            return None

        try:
            default_count = int(default_count_str)
        except ValueError:
            self.show_error("Invalid number for default count")
            return None

        return BundleData(
            bundle_id=bundle_id,
            description=description,
            default_count=default_count
        )

    def prompt_edit_bundle_metadata(
        self,
        current_description: str,
        current_default_count: int
    ) -> Optional[Dict[str, any]]:
        """
        Prompt user to edit bundle metadata.

        Args:
            current_description: Current description
            current_default_count: Current default count

        Returns:
            Dictionary with updated values or None if cancelled
        """
        print("\n--- Edit Bundle Metadata ---")
        print(f"  Current description: {current_description}")
        print(f"  Current default count: {current_default_count}\n")

        # New description
        new_description = questionary.text(
            "  New description (or press Enter to keep current):",
            default=current_description,
            style=self.style,
            qmark="",
        ).ask()

        if new_description is None:
            return None

        # New default count
        new_count_str = questionary.text(
            "  New default count (or press Enter to keep current):",
            default=str(current_default_count),
            style=self.style,
            qmark="",
        ).ask()

        if new_count_str is None:
            return None

        try:
            new_count = int(new_count_str)
        except ValueError:
            self.show_error("Invalid number for default count")
            return None

        return {
            'description': new_description if new_description != current_description else None,
            'default_count': new_count if new_count != current_default_count else None
        }

    def prompt_select_bundle(
        self,
        bundles: List[Dict[str, any]],
        message: str = "  Select a bundle:",
        show_cancel: bool = True
    ) -> Optional[str]:
        """
        Prompt user to select a bundle from list.

        Args:
            bundles: List of bundle dictionaries
            message: Prompt message
            show_cancel: Whether to show cancel option

        Returns:
            Selected bundle_id or None if cancelled
        """
        if not bundles:
            self.show_info("No bundles available")
            return None

        choices = []

        for bundle in bundles:
            label = f"  {bundle['bundle_id']:20} ({bundle['source_count']} sources)"
            choices.append(questionary.Choice(label, bundle['bundle_id']))

        if show_cancel:
            choices.append(questionary.Separator())
            choices.append(questionary.Choice("Cancel", "cancel"))

        selected = questionary.select(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
        ).ask()

        return None if selected == "cancel" else selected

    def prompt_select_sources(
        self,
        sources: Dict[str, str],
        current_selections: List[str] = None,
        message: str = "  Select sources:",
        group_by_category: bool = True
    ) -> Optional[List[str]]:
        """
        Prompt user to multi-select sources.

        Args:
            sources: Dict of source_id -> display_name
            current_selections: Pre-selected source IDs
            message: Prompt message
            group_by_category: Whether to group sources by category

        Returns:
            List of selected source IDs or None if cancelled
        """
        from core.source_system.source_registry import get_source_registry

        if current_selections is None:
            current_selections = []

        if not sources:
            self.show_info("No sources available")
            return None

        choices = []

        if group_by_category:
            # Group sources by category
            registry = get_source_registry()
            categories = {}

            for source_id, display_name in sources.items():
                config = registry.get_source_config(source_id)
                category = getattr(config, 'category', 'other') if config else 'other'
                if category not in categories:
                    categories[category] = []
                categories[category].append((source_id, display_name))

            # Build choices with category headers
            for category, category_sources in sorted(categories.items()):
                choices.append(questionary.Separator(f"\n  {category.upper()}"))
                for source_id, display_name in sorted(category_sources):
                    label = f"  {source_id:15} → {display_name}"
                    choices.append(questionary.Choice(
                        label,
                        source_id,
                        checked=source_id in current_selections
                    ))
        else:
            # Simple list
            for source_id, display_name in sorted(sources.items()):
                label = f"  {source_id:15} → {display_name}"
                choices.append(questionary.Choice(
                    label,
                    source_id,
                    checked=source_id in current_selections
                ))

        selected = questionary.checkbox(
            message,
            choices=choices,
            style=self.style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use Space to select, Enter to confirm)",
        ).ask()

        return selected if selected is not None else None

    def prompt_copy_or_move(self) -> Optional[str]:
        """
        Prompt user to choose between copy and move mode.

        Returns:
            'copy' or 'move' or None if cancelled
        """
        return questionary.select(
            "  Copy or Move?",
            choices=[
                questionary.Choice("Copy (keep in source bundle)", "copy"),
                questionary.Choice("Move (remove from source bundle)", "move"),
                questionary.Separator(),
                questionary.Choice("Cancel", "cancel"),
            ],
            style=self.style,
            qmark="",
            pointer="▶",
        ).ask()

    def show_bundle_details(self, bundle_info: Dict[str, any]) -> None:
        """
        Display detailed bundle information.

        Args:
            bundle_info: Bundle information dictionary
        """
        print("\n" + "─" * 70)
        print(f"\033[38;5;202m  Bundle Details\033[0m")
        print("─" * 70)

        print(f"\n  \033[1mID:\033[0m             {bundle_info['bundle_id']}")
        print(f"  \033[1mDescription:\033[0m    {bundle_info['description']}")
        print(f"  \033[1mDefault Count:\033[0m  {bundle_info['default_count']}")
        print(f"  \033[1mTotal Sources:\033[0m  {bundle_info['total_sources']}")

        if bundle_info.get('category_distribution'):
            print(f"\n  \033[1mCategory Distribution:\033[0m")
            for category, count in sorted(bundle_info['category_distribution'].items()):
                print(f"    {category:15} {count} sources")

        if bundle_info.get('sources'):
            print(f"\n  \033[1mSources:\033[0m")
            for source_id in sorted(bundle_info['sources']):
                print(f"    • {source_id}")

        print("\n" + "─" * 70)
        input("\n  Press Enter to continue...")

    def show_all_bundles(self, bundles: List[Dict[str, any]]) -> None:
        """
        Display all bundles in a formatted list.

        Args:
            bundles: List of bundle dictionaries
        """
        print("\n" + "─" * 70)
        print(f"\033[38;5;202m  All Bundles ({len(bundles)} total)\033[0m")
        print("─" * 70)

        if not bundles:
            print("\n  No bundles available")
        else:
            print(f"\n  {'Bundle ID':<20} {'Sources':<10} {'Default Count':<15} Description")
            print("  " + "─" * 66)

            for bundle in bundles:
                print(
                    f"  {bundle['bundle_id']:<20} "
                    f"{bundle['source_count']:<10} "
                    f"{bundle['default_count']:<15} "
                    f"{bundle['description']}"
                )

        print("\n" + "─" * 70)
        input("\n  Press Enter to continue...")

    def prompt_confirm(
        self,
        message: str,
        details: List[str] = None,
        default: bool = False
    ) -> bool:
        """
        Prompt user for confirmation.

        Args:
            message: Confirmation question
            details: Optional list of detail lines to show
            default: Default response

        Returns:
            True if confirmed, False otherwise
        """
        if details:
            print()
            for detail in details:
                print(f"  {detail}")
            print()

        return questionary.confirm(
            f"  {message}",
            default=default,
            style=self.style,
            qmark="",
        ).ask()

    def show_success(self, message: str) -> None:
        """Display success message."""
        print(f"\n  \033[32m✓\033[0m {message}")

    def show_error(self, message: str) -> None:
        """Display error message."""
        print(f"\n  \033[31m✗\033[0m {message}")

    def show_info(self, message: str) -> None:
        """Display informational message."""
        print(f"\n  ℹ {message}")

    def show_warning(self, message: str) -> None:
        """Display warning message."""
        print(f"\n  \033[33m⚠\033[0m {message}")
