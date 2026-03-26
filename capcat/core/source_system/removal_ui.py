"""
User interface implementation for remove-source command.
Follows the same clean styling as add-source with orange theme.
"""

from typing import List
import sys
from prompt_toolkit.styles import Style

from capcat.core.source_system.remove_source_command import (
    SourceRemovalInfo
)

# Custom style matching Capcat catch menu
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),  # Orange question mark
    ('question', 'bold'),                 # Bold question text
    ('selected', 'fg:#d75f00'),          # Orange for selected option
    ('pointer', 'fg:#d75f00 bold'),      # Orange pointer
    ('answer', 'fg:#d75f00'),            # Orange answer
    ('instruction', ''),                  # Instruction text
])


class QuestionaryRemovalUI:
    """
    Interactive UI for remove-source using questionary.
    Matches the styling of add-source and catch menu.
    """

    def __init__(self, questionary_module=None):
        """
        Initialize with optional questionary module.

        Args:
            questionary_module: Optional questionary for testing
        """
        self._questionary = questionary_module
        if self._questionary is None:
            import questionary
            self._questionary = questionary

    def select_sources_to_remove(
        self, sources: List[tuple[str, str]]
    ) -> List[str]:
        """
        Let user select sources to remove using checkbox.

        Args:
            sources: List of (source_id, display_name) tuples

        Returns:
            List of selected source IDs
        """
        if not sources:
            return []

        # Create choices with display names
        choices = [
            self._questionary.Choice(f"{name} ({sid})", sid)
            for sid, name in sources
        ]

        selected = self._questionary.checkbox(
            "  Select sources to remove (use <space> to select):",
            choices=choices,
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Press Ctrl+C to cancel)"
        ).ask()

        return selected if selected is not None else []

    def show_removal_summary(
        self, sources_info: List[SourceRemovalInfo]
    ) -> None:
        """
        Display summary of what will be removed.

        Args:
            sources_info: Information about sources to be removed
        """
        print("\n--- Removal Summary ---")

        for info in sources_info:
            print(f"\n  Source: {info.display_name} ({info.source_id})")
            print(f"  Config: {info.config_path}")

            if info.bundles:
                print(f"  Bundles: {', '.join(info.bundles)}")
            else:
                print("  Bundles: (none)")

        print("\n" + "-" * 50)

    def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool:
        """
        Confirm removal with user.

        Args:
            sources_info: Sources to be removed

        Returns:
            True if confirmed, False otherwise
        """
        count = len(sources_info)
        result = self._questionary.confirm(
            f"  Remove {count} source(s)? This cannot be undone.",
            default=False,
            style=custom_style,
            qmark=""
        ).ask()

        return result if result is not None else False

    def show_success(self, message: str) -> None:
        """Display success message."""
        print(f"✓ {message}")

    def show_error(self, message: str) -> None:
        """Display error message."""
        print(f"Error: {message}", file=sys.stderr)

    def show_info(self, message: str) -> None:
        """Display informational message."""
        print(message)


class MockRemovalUI:
    """Mock UI for testing remove-source."""

    def __init__(self, responses: dict):
        """
        Initialize with predefined responses.

        Args:
            responses: Dictionary with test responses
        """
        self.responses = responses
        self.calls = []

    def select_sources_to_remove(
        self, sources: List[tuple[str, str]]
    ) -> List[str]:
        """Record call and return the configured selected_sources response.

        Args:
            sources: List of ``(source_id, display_name)`` tuples.

        Returns:
            ``responses['selected_sources']`` if set, otherwise ``[]``.
        """
        self.calls.append(('select_sources_to_remove', sources))
        return self.responses.get('selected_sources', [])

    def show_removal_summary(
        self, sources_info: List[SourceRemovalInfo]
    ) -> None:
        """Record call without printing the summary.

        Args:
            sources_info: Source removal info objects passed by the workflow.
        """
        self.calls.append(('show_removal_summary', sources_info))

    def confirm_removal(self, sources_info: List[SourceRemovalInfo]) -> bool:
        """Record call and return the configured confirm_removal response.

        Args:
            sources_info: Source removal info objects passed by the workflow.

        Returns:
            ``responses['confirm_removal']`` if set, otherwise ``False``.
        """
        self.calls.append(('confirm_removal', sources_info))
        return self.responses.get('confirm_removal', False)

    def show_success(self, message: str) -> None:
        """Record success message call without producing output.

        Args:
            message: Success message passed by the workflow.
        """
        self.calls.append(('show_success', message))

    def show_error(self, message: str) -> None:
        """Record error message call without producing output.

        Args:
            message: Error message passed by the workflow.
        """
        self.calls.append(('show_error', message))

    def show_info(self, message: str) -> None:
        """Record info message call without producing output.

        Args:
            message: Informational message passed by the workflow.
        """
        self.calls.append(('show_info', message))