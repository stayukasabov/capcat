#!/usr/bin/env python3
"""
Interactive mode for Capcat.
"""

from prompt_toolkit.styles import Style
import questionary

# Custom style for questionary
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),  # Orange question mark
    ('question', 'bold'),                 # Bold question text
    ('selected', 'fg:#d75f00'),          # Orange for selected option
    ('pointer', 'fg:#d75f00 bold'),      # Orange pointer
    ('answer', 'fg:#d75f00'),            # Orange answer
    ('instruction', ''),                  # Instruction text
])
import subprocess
import sys
import os
import logging
import contextlib
import shutil

from capcat import run_app


@contextlib.contextmanager
def suppress_logging():
    """A context manager to temporarily suppress logging."""
    logger = logging.getLogger()
    original_level = logger.level
    logger.setLevel(logging.CRITICAL)
    try:
        yield
    finally:
        logger.setLevel(original_level)

def position_menu_at_bottom(menu_lines=10):
    """
    Position cursor for bottom-aligned menu display.

    Args:
        menu_lines: Number of lines the menu will occupy (default: 10)
    """
    try:
        terminal_size = shutil.get_terminal_size()
        terminal_height = terminal_size.lines

        # Clear screen
        print('\033[2J', end='')

        # ASCII art logo
        logo = """\033[38;5;202m

       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \ / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \_____\__,_|  __/ \___\__,_|\__|
                | |
                |_|\033[0m
"""

        # Calculate padding needed to push menu to bottom
        # Reserve space for logo (8 lines) + menu lines plus some padding
        logo_lines = 8
        padding_lines = max(0, terminal_height - menu_lines - logo_lines - 1)

        # Move cursor to home, print logo, then add padding
        print('\033[H' + logo + '\n' * padding_lines, end='')

    except Exception:
        # Fallback to standard clear if terminal size detection fails
        print('\033[2J\033[H', end='')

def start_interactive_mode():
    """Starts the interactive user interface."""
    first_run = True
    while True:
        # Position menu at bottom of terminal (main menu: ~10 lines)
        position_menu_at_bottom(menu_lines=10)

        with suppress_logging():
            prompt_text = "  What would you like me to do?" if first_run else "  Select an option:"
            action = questionary.select(
                prompt_text,
                choices=[
                    questionary.Choice("Catch articles from a bundle of sources", "bundle"),
                    questionary.Choice("Catch articles from a list of sources", "fetch"),
                    questionary.Choice("Catch from a single source", "single_source"),
                    questionary.Choice("Catch a single article by URL", "single_url"),
                    questionary.Choice("Manage Sources (add/remove/configure)", "manage_sources"),
                    questionary.Choice("Exit", "exit"),
                ],
                style=custom_style,
                qmark="",
                pointer="▶",
                instruction="\n   (Use arrow keys to navigate)",
            ).ask()

        first_run = False

        if not action or action == 'exit':
            print("Exiting interactive mode.")
            return

        # Clear questionary's selection echo and show our own
        action_names = {
            'bundle': 'Catch articles from a bundle of sources',
            'fetch': 'Catch articles from a list of sources',
            'single_source': 'Catch from a single source',
            'single_url': 'Catch a single article by URL',
            'manage_sources': 'Manage Sources (add/remove/configure)'
        }
        # Move cursor up one line and clear it, then print our message
        print('\033[F\033[K', end='')
        print(f"  Selected option: {action_names.get(action, action)}")

        if action == 'bundle':
            _handle_bundle_flow()
        elif action == 'fetch':
            _handle_fetch_flow()
        elif action == 'single_source':
            _handle_single_source_flow()
        elif action == 'single_url':
            _handle_single_url_flow()
        elif action == 'manage_sources':
            _handle_manage_sources_flow()

def _handle_manage_sources_flow():
    """Handles the logic for source management submenu."""
    while True:
        with suppress_logging():
            action = questionary.select(
                "  Source Management - Select an option:",
                choices=[
                    questionary.Choice("Add New Source from RSS Feed", "add_rss"),
                    questionary.Choice("Generate Custom Source Config", "generate_config"),
                    questionary.Choice("Remove Existing Sources", "remove"),
                    questionary.Choice("List All Sources", "list_sources"),
                    questionary.Choice("Test a Source", "test_source"),
                    questionary.Choice("Manage Bundles", "manage_bundles"),
                    questionary.Separator(),
                    questionary.Choice("Back to Main Menu", "back"),
                ],
                style=custom_style,
                qmark="",
                pointer="▶",
                instruction="\n   (Use arrow keys to navigate)",
            ).ask()

        if not action or action == 'back':
            return

        if action == 'add_rss':
            _handle_add_source_from_rss()
        elif action == 'generate_config':
            _handle_generate_config()
        elif action == 'remove':
            _handle_remove_source()
        elif action == 'list_sources':
            _handle_list_sources()
        elif action == 'test_source':
            _handle_test_source()
        elif action == 'manage_bundles':
            _handle_manage_bundles()


def _handle_add_source_from_rss():
    """Handle adding a new source from RSS feed."""
    print("  (Use Ctrl+C to go back)")
    with suppress_logging():
        url = questionary.text(
            "  Enter the RSS feed URL:",
            style=custom_style,
            qmark="",
        ).ask()

    if not url:
        print("  No URL provided. Returning to menu.")
        return

    # Call the existing add_source function from cli
    try:
        from cli import add_source, get_available_sources
        add_source(url)

        # Show updated source count
        sources = get_available_sources()
        print(f"\n✓ Active sources: {len(sources)}")

    except Exception as e:
        print(f"Error adding source: {e}")

    input("\nPress Enter to continue...")


def _handle_generate_config():
    """Handle generating a custom source config."""
    print("\n--- Generate Custom Source Configuration ---")
    print("This will launch the interactive config generator.\n")

    with suppress_logging():
        confirm = questionary.confirm(
            "  Continue?",
            default=True,
            style=custom_style,
            qmark="",
        ).ask()

    if not confirm:
        return

    # Launch the config generator script
    try:
        import subprocess
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "scripts",
            "generate_source_config.py"
        )

        result = subprocess.run([sys.executable, script_path], check=False)

        if result.returncode != 0:
            print(f"\nConfig generation exited with code: {result.returncode}")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f"Error launching config generator: {e}")
        input("\nPress Enter to continue...")


def _handle_remove_source():
    """Handle removing existing sources."""
    print("\n--- Remove Sources ---")
    print("This will launch the interactive source removal tool.\n")

    # Use the existing remove-source service
    try:
        from core.source_system.remove_source_service import create_remove_source_service
        from core.source_system.enhanced_remove_command import RemovalOptions

        service = create_remove_source_service()
        command = service._create_remove_source_command()

        # Simple interactive removal
        options = RemovalOptions(
            dry_run=False,
            create_backup=True,
            show_analytics=True,
            batch_file=None,
            force=False
        )

        from core.source_system.removal_ui import QuestionaryRemovalUI
        from core.source_system.enhanced_remove_command import EnhancedRemoveCommand
        from core.source_system.source_backup_manager import SourceBackupManager
        from core.source_system.source_analytics import SourceAnalytics
        from core.logging_config import get_logger

        enhanced_command = EnhancedRemoveCommand(
            base_command=command,
            backup_manager=SourceBackupManager(),
            analytics=SourceAnalytics(),
            ui=QuestionaryRemovalUI(),
            logger=get_logger(__name__)
        )

        enhanced_command.execute_with_options(options)

        # Show updated source count
        from cli import get_available_sources
        sources = get_available_sources()
        print(f"\n✓ Active sources: {len(sources)}")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f"Error removing sources: {e}")
        input("\nPress Enter to continue...")


def _handle_list_sources():
    """Handle listing all available sources."""
    from cli import get_available_sources
    from core.source_system.source_registry import get_source_registry

    sources = get_available_sources()
    registry = get_source_registry()

    # Group by category
    categories = {}
    for source_id, display_name in sorted(sources.items()):
        try:
            config = registry.get_source_config(source_id)
            category = config.category if config and hasattr(config, 'category') else 'other'
        except:
            category = 'other'

        if category not in categories:
            categories[category] = []

        categories[category].append((source_id, display_name))

    # Build formatted choices for questionary
    choices = []

    # Header with count
    choices.append(questionary.Separator(f"\n  Available Sources ({len(sources)} total)"))
    choices.append(questionary.Separator())

    # Display grouped sources
    for category, source_list in sorted(categories.items()):
        # Category header
        choices.append(questionary.Separator(f"  {category.upper()}"))

        # Sources in category
        for source_id, display_name in source_list:
            # Format: "source_id → Display Name"
            formatted_name = f"  {source_id:15} → {display_name}"
            choices.append(questionary.Choice(formatted_name, source_id))

        # Blank line between categories
        choices.append(questionary.Separator())

    # Back option
    choices.append(questionary.Separator("─" * 50))
    choices.append(questionary.Choice("Back to Source Management", "back"))

    # Show interactive list
    with suppress_logging():
        selected = questionary.select(
            "  Browse sources (select to view details):",
            choices=choices,
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys, Enter to view details)",
        ).ask()

    # If a source was selected (not back), show its details
    if selected and selected != 'back':
        _show_source_details(selected, registry)
        _handle_list_sources()  # Return to listing


def _show_source_details(source_id, registry):
    """Display detailed information about a source."""
    print("\n" + "─" * 70)
    print(f"\033[38;5;202m  Source Details\033[0m")
    print("─" * 70)

    try:
        config = registry.get_source_config(source_id)

        if not config:
            print(f"\n  Source '{source_id}' not found in registry.")
            input("\n  Press Enter to continue...")
            return

        # Display core information
        print(f"\n  \033[1mID:\033[0m           {source_id}")
        print(f"  \033[1mName:\033[0m         {getattr(config, 'display_name', 'N/A')}")
        print(f"  \033[1mCategory:\033[0m     {getattr(config, 'category', 'N/A')}")

        # Base URL
        if hasattr(config, 'base_url'):
            print(f"  \033[1mBase URL:\033[0m     {config.base_url}")

        # Discovery method
        if hasattr(config, 'discovery') and hasattr(config.discovery, 'method'):
            print(f"  \033[1mDiscovery:\033[0m    {config.discovery.method}")

            # RSS URLs if available
            if config.discovery.method == 'rss' and hasattr(config.discovery, 'rss_urls'):
                rss_urls = config.discovery.rss_urls
                if hasattr(rss_urls, 'primary'):
                    print(f"  \033[1mRSS Feed:\033[0m     {rss_urls.primary}")

        # Source type (config-driven vs custom)
        source_type = "Config-driven (YAML)" if hasattr(config, 'article_selectors') else "Custom (Python)"
        print(f"  \033[1mType:\033[0m         {source_type}")

        print("\n" + "─" * 70)

    except Exception as e:
        print(f"\n  Error loading source details: {e}")

    input("\n  Press Enter to continue...")


def _handle_test_source():
    """Handle testing a source."""
    from cli import get_available_sources

    sources = get_available_sources()
    source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
    source_choices.append(questionary.Separator())
    source_choices.append(questionary.Choice("Back", "back"))

    with suppress_logging():
        source_id = questionary.select(
            "  Select source to test:",
            choices=source_choices,
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    if not source_id or source_id == 'back':
        return

    print(f"\n--- Testing Source: {source_id} ---")
    print("Fetching 3 articles...\n")

    # Test fetch using the run_app function
    try:
        from capcat import run_app
        args = ['fetch', source_id, '--count', '3']
        run_app(args)
        print(f"\n✓ Source '{source_id}' test completed")
    except SystemExit as e:
        if e.code != 0:
            print(f"\n✗ Source test failed with code: {e.code}")
    except Exception as e:
        print(f"\n✗ Error testing source: {e}")

    input("\nPress Enter to continue...")


def _handle_bundle_flow():
    """Handles the logic for the bundle selection flow."""
    # Position menu at bottom (bundle menu can be long)
    position_menu_at_bottom(menu_lines=15)

    from cli import get_available_bundles, get_available_sources
    from core.source_system.source_registry import get_source_registry

    bundles = get_available_bundles()
    all_sources_map = get_available_sources()
    registry = get_source_registry()

    bundle_choices = []
    for name, data in bundles.items():
        description = data.get("description", "")

        # Don't list sources for the 'all' bundle
        if name == "all":
            full_description = description
        else:
            # Start with sources explicitly listed in bundles.yml
            bundle_sources = data.get("sources", [])

            # Auto-discover sources with matching category that aren't in bundles.yml
            category_sources = registry.get_sources_by_category(name)
            for source_id in category_sources:
                if source_id not in bundle_sources:
                    bundle_sources.append(source_id)

            # Get display names for all sources
            source_names = [all_sources_map.get(sid, sid) for sid in bundle_sources]
            # Add a newline and indentation for better readability
            sources_str = f"\n   ({', '.join(source_names)})" if source_names else ""
            full_description = f"{description}{sources_str}"

        bundle_choices.append(questionary.Choice(f"{name} - {full_description}", name))

    bundle_choices.append(questionary.Separator())
    bundle_choices.append(questionary.Choice("Back to Main Menu", "back"))

    with suppress_logging():
        bundle = questionary.select(
            "  Select a news bundle and hit Enter for activation.",
            choices=bundle_choices,
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    if bundle is None or bundle == 'back':
        return

    if bundle:
        _prompt_for_html('bundle', bundle)

def _handle_fetch_flow():
    """Handles the logic for the fetch (multi-source) flow."""
    # Position menu at bottom (source list can be long)
    position_menu_at_bottom(menu_lines=15)

    from cli import get_available_sources
    sources = get_available_sources()

    source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
    source_choices.append(questionary.Separator())
    source_choices.append(questionary.Choice("Back to Main Menu", "back"))

    with suppress_logging():
        selected_sources = questionary.checkbox(
            "  Select sources (Space to select, Enter to confirm):",
            choices=source_choices,
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use Space to select multiple sources, Enter to confirm)",
        ).ask()

    if selected_sources is None or 'back' in selected_sources:
        return

    if selected_sources:
        _prompt_for_html('fetch', selected_sources)

def _handle_single_source_flow():
    """Handles the logic for the single source selection flow."""
    # Position menu at bottom (source list can be long)
    position_menu_at_bottom(menu_lines=15)

    from cli import get_available_sources
    sources = get_available_sources()

    source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
    source_choices.append(questionary.Separator())
    source_choices.append(questionary.Choice("Back to Main Menu", "back"))

    with suppress_logging():
        source = questionary.select(
            "  Select a source and hit Enter for activation.",
            choices=source_choices,
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    if source is None or source == 'back':
        return

    if source:
        # For single source, we still call fetch but with just one source
        _prompt_for_html('fetch', [source])

def _handle_single_url_flow():
    """Handles the logic for the single URL flow."""
    # Position menu at bottom (URL input prompt)
    position_menu_at_bottom(menu_lines=5)

    print("  (Use Ctrl+C to go to the Main Menu)")
    with suppress_logging():
        url = questionary.text(
            "  Please enter the article URL:",
            style=custom_style,
            qmark="",
        ).ask()

    if url is None:
        return

    if url:
        _prompt_for_html('single', url)
    else:
        with suppress_logging():
            repeat = questionary.confirm(
                "  No URL entered. Would you like to try again?",
                default=True,
                style=custom_style,
                qmark="",
            ).ask()
        if repeat:
            _handle_single_url_flow()

def _prompt_for_html(action, selection):
    """Prompts for HTML generation."""
    # Position menu at bottom (HTML prompt is short)
    position_menu_at_bottom(menu_lines=8)

    with suppress_logging():
        response = questionary.select(
            "  Generate HTML for web browsing?",
            choices=[
                questionary.Choice("Yes", "yes"),
                questionary.Choice("No", "no"),
                questionary.Separator(),
                questionary.Choice("Back to Main Menu", "back"),
            ],
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    if response is None or response == 'back':
        return

    generate_html = response == "yes"
    _confirm_and_execute(action, selection, generate_html)

def _confirm_and_execute(action, selection, generate_html):
    """Prints a summary and executes the command by calling run_app directly."""
    summary = f"Action: {action}\n"
    if action == 'bundle':
        summary += f"Bundle: {selection}\n"
    elif action == 'fetch':
        summary += f"Sources: {', '.join(selection)}\n"
    elif action == 'single':
        summary += f"URL: {selection}\n"

    summary += f"Generate HTML: {generate_html}\n"

    print("--------------------")
    print("SUMMARY")
    print(summary)
    print("--------------------")

    # Construct the argument list for run_app
    args = [action]

    if action == 'bundle':
        args.append(selection)
    elif action == 'fetch':
        args.append(','.join(selection))
    elif action == 'single':
        args.append(selection)

    if generate_html:
        args.append('--html')

    try:
        print("Executing command...")
        run_app(args)
    except SystemExit as e:
        # The run_app function calls sys.exit(), which we intercept.
        if e.code != 0:
            print(f"Command finished with error code: {e.code}")
            # Re-exit with error code so wrapper script sees the failure
            sys.exit(e.code)
        # On success (code 0), continue - don't exit interactive mode

    # Pause so user can see output before returning to menu
    input("\nPress Enter to return to main menu...")


def _handle_manage_bundles():
    """Handle bundle management submenu."""
    from pathlib import Path
    from core.source_system.bundle_service import BundleService

    bundles_path = Path(__file__).parent.parent / "sources" / "active" / "bundles.yml"
    service = BundleService(bundles_path)

    while True:
        action = service.ui.show_bundle_menu()

        if not action or action == 'back':
            return

        if action == 'create':
            service.execute_create_bundle()
        elif action == 'edit':
            service.execute_edit_bundle()
        elif action == 'delete':
            service.execute_delete_bundle()
        elif action == 'add_sources':
            service.execute_add_sources()
        elif action == 'remove_sources':
            service.execute_remove_sources()
        elif action == 'move_sources':
            service.execute_move_source()
        elif action == 'list':
            service.execute_list_bundles()
