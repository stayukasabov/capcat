"""
User interface implementation using questionary for interactive prompts.
Implements the UserInterface protocol for clean separation of concerns.
"""

from typing import List, Optional
import sys
from prompt_toolkit.styles import Style


# Custom style matching Capcat catch menu
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),  # Orange question mark
    ('question', 'bold'),                 # Bold question text
    ('selected', 'fg:#d75f00'),          # Orange for selected option
    ('pointer', 'fg:#d75f00 bold'),      # Orange pointer
    ('answer', 'fg:#d75f00'),            # Orange answer
    ('instruction', ''),                  # Instruction text
])


class QuestionaryUserInterface:
    """
    Interactive user interface using questionary library.
    Handles all user interactions for the add-source command.
    """

    def __init__(self, questionary_module=None):
        """
        Initialize with optional questionary module for dependency injection.

        Args:
            questionary_module: Optional questionary module for testing
        """
        self._questionary = questionary_module
        if self._questionary is None:
            import questionary
            self._questionary = questionary

    def get_display_name(self, suggested: str) -> str:
        """
        Get display name from user with feed title as suggestion.

        Args:
            suggested: Feed title from RSS feed

        Returns:
            User-entered display name
        """
        name = self._questionary.text(
            "  Display name:",
            default=suggested,
            style=custom_style,
            qmark=""
        ).ask()

        if not name:
            self.show_error("Display name cannot be empty.")
            sys.exit(1)

        return name

    def get_source_id(self, suggested: str) -> str:
        """
        Get source ID from user with suggestion.

        Args:
            suggested: Suggested source ID based on feed title

        Returns:
            User-entered source ID

        Raises:
            SystemExit: If user cancels or provides empty input
        """
        source_id = self._questionary.text(
            "  Source ID (alphanumeric):",
            default=suggested,
            style=custom_style,
            qmark=""
        ).ask()

        if not source_id:
            self.show_error("Source ID cannot be empty.")
            sys.exit(1)

        return source_id

    def select_category(self, categories: List[str]) -> str:
        """
        Let user select a category from available options.

        Args:
            categories: List of available categories

        Returns:
            Selected category

        Raises:
            SystemExit: If user cancels selection
        """
        if not categories:
            self.show_error("No categories available.")
            sys.exit(1)

        category = self._questionary.select(
            "  Select category:",
            choices=categories,
            use_indicator=True,
            style=custom_style,
            qmark="",
            pointer="▶"
        ).ask()

        if not category:
            self.show_error("Category selection cancelled.")
            sys.exit(1)

        return category

    def get_article_count(self) -> int:
        """Ask how many articles to fetch per run."""
        while True:
            raw = self._questionary.text(
                "  How many articles should this source fetch per run?",
                default="30",
                style=custom_style,
                qmark="",
            ).ask()
            if raw is None:
                return 30  # cancelled
            raw = raw.strip()
            if not raw:
                return 30
            try:
                count = int(raw)
                if count > 0:
                    return count
            except ValueError:
                pass
            print("  Please enter a positive number.")

    def confirm_bundle_addition(self) -> bool:
        """
        Ask user if they want to add source to a bundle.

        Returns:
            True if user wants to add to bundle, False otherwise
        """
        result = self._questionary.confirm(
            "  Add to bundle?",
            style=custom_style,
            qmark=""
        ).ask()
        return result if result is not None else False

    def select_bundle(self, bundles: List[str]) -> Optional[str]:
        """
        Let user select a bundle from available options.

        Args:
            bundles: List of available bundle names

        Returns:
            Selected bundle name or None if cancelled
        """
        if not bundles:
            self.show_error("No bundles available.")
            return None

        return self._questionary.select(
            "  Select bundle:",
            choices=bundles,
            use_indicator=True,
            style=custom_style,
            qmark="",
            pointer="▶"
        ).ask()

    def confirm_test_fetch(self) -> bool:
        """
        Ask user if they want to run a test fetch.

        Returns:
            True if user wants to test, False otherwise
        """
        result = self._questionary.confirm(
            "  Test fetch? (recommended)",
            style=custom_style,
            qmark=""
        ).ask()
        return result if result is not None else False

    def show_success(self, message: str) -> None:
        """
        Display success message to user.

        Args:
            message: Success message to display
        """
        print(f"✓ {message}")

    def show_error(self, message: str) -> None:
        """
        Display error message to user.

        Args:
            message: Error message to display
        """
        print(f"Error: {message}", file=sys.stderr)

    def show_info(self, message: str) -> None:
        """
        Display informational message to user.

        Args:
            message: Info message to display
        """
        print(message)


class MockUserInterface:
    """
    Mock user interface for testing purposes.
    Provides predictable responses for automated testing.
    """

    def __init__(self, responses: dict = None):
        """
        Initialize with predefined responses.

        Args:
            responses: Dictionary mapping method names to return values
        """
        self.responses = responses if responses is not None else {}
        self.calls = []

    def get_display_name(self, suggested: str) -> str:
        """Record call and return the configured display_name response.

        Args:
            suggested: Feed title passed by the workflow.

        Returns:
            ``responses['display_name']`` if set, otherwise *suggested*.
        """
        self.calls.append(('get_display_name', suggested))
        return self.responses.get('display_name', suggested)

    def get_source_id(self, suggested: str) -> str:
        """Record call and return the configured source_id response.

        Args:
            suggested: Suggested source ID passed by the workflow.

        Returns:
            ``responses['source_id']`` if set, otherwise *suggested*.
        """
        self.calls.append(('get_source_id', suggested))
        return self.responses.get('source_id', suggested)

    def select_category(self, categories: List[str]) -> str:
        """Record call and return the configured category response.

        Args:
            categories: Available category names.

        Returns:
            ``responses['category']`` if set, otherwise the first category or
            ``'tech'`` when the list is empty.
        """
        self.calls.append(('select_category', categories))
        return self.responses.get('category', categories[0] if categories else 'tech')

    def get_article_count(self) -> int:
        self.calls.append(('get_article_count',))
        return self.responses.get('article_count', 30)

    def confirm_bundle_addition(self) -> bool:
        """Record call and return the configured confirm_bundle response.

        Returns:
            ``responses['confirm_bundle']`` if set, otherwise ``False``.
        """
        self.calls.append(('confirm_bundle_addition',))
        return self.responses.get('confirm_bundle', False)

    def select_bundle(self, bundles: List[str]) -> Optional[str]:
        """Record call and return the configured bundle response.

        Args:
            bundles: Available bundle names.

        Returns:
            ``responses['bundle']`` if set, otherwise the first bundle or
            ``None`` when the list is empty.
        """
        self.calls.append(('select_bundle', bundles))
        return self.responses.get('bundle', bundles[0] if bundles else None)

    def confirm_test_fetch(self) -> bool:
        """Record call and return the configured confirm_test response.

        Returns:
            ``responses['confirm_test']`` if set, otherwise ``False``.
        """
        self.calls.append(('confirm_test_fetch',))
        return self.responses.get('confirm_test', False)

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