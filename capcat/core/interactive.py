#!/usr/bin/env python3
"""
Interactive mode for Capcat.
"""

import contextlib
import logging
import os
import shutil
import sys

from prompt_toolkit.styles import Style
import questionary

from capcat.core.source_system.bundle_service import get_available_sources
from capcat.core.source_system.source_registry import get_source_registry

# Custom style for questionary
custom_style = Style([
    ('questionmark', 'fg:#d75f00 bold'),  # Orange question mark
    ('question', 'bold'),                 # Bold question text
    ('selected', 'fg:#d75f00'),          # Orange for selected option
    ('pointer', 'fg:#d75f00 bold'),      # Orange pointer
    ('answer', 'fg:#d75f00'),            # Orange answer
    ('instruction', ''),                  # Instruction text
])


LOGO = (
    "\n\n"
    "       ____\n"
    "     / ____|                     _\n"
    "    | |     __ _ _ __   ___ __ _| |_\n"
    "    | |    / _  |  _ \\ / __/ _  | __|\n"
    "    | |___| (_| | |_) | (_| (_| | |_\n"
    "     \\_____\\__,_|  __/ \\___\\__,_\\__|\n"
    "                | |\n"
    "                |_|"
)


_LOGO_ROWS = 10  # rows consumed by print(LOGO): 2 blank + 8 art + print's \n


def print_logo(menu_lines=0):
    print('\033[2J\033[H', end='')
    print('\033[38;5;202m' + LOGO + '\033[0m')
    if menu_lines > 0:
        try:
            terminal_height = shutil.get_terminal_size().lines
            padding = max(1, terminal_height - menu_lines - _LOGO_ROWS)
        except Exception:
            padding = 2
    else:
        padding = 2
    print('\n' * (padding - 1))


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

def start_interactive_mode():
    """Starts the interactive user interface."""
    first_run = True
    while True:
        print_logo(menu_lines=9)
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
        print_logo(menu_lines=10)
        with suppress_logging():
            action = questionary.select(
                "  Source Management - Select an option:",
                choices=[
                    questionary.Choice("Add New Source from RSS Feed", "add_rss"),
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
        from capcat.commands.add_source import add_source
        from capcat.core.source_system.bundle_service import get_available_sources
        from capcat.core.source_system.source_registry import reset_source_registry
        add_source(url)
        reset_source_registry()

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
        from capcat.core.source_system.remove_source_service import create_remove_source_service
        from capcat.core.source_system.enhanced_remove_command import RemovalOptions

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

        from capcat.core.source_system.removal_ui import QuestionaryRemovalUI
        from capcat.core.source_system.enhanced_remove_command import EnhancedRemoveCommand
        from capcat.core.source_system.source_backup_manager import SourceBackupManager
        from capcat.core.source_system.source_analytics import SourceAnalytics
        from capcat.core.logging_config import get_logger

        enhanced_command = EnhancedRemoveCommand(
            base_command=command,
            backup_manager=SourceBackupManager(),
            analytics=SourceAnalytics(),
            ui=QuestionaryRemovalUI(),
            logger=get_logger(__name__)
        )

        enhanced_command.execute_with_options(options)

        # Show updated source count
        from capcat.core.source_system.bundle_service import get_available_sources
        sources = get_available_sources()
        print(f"\n✓ Active sources: {len(sources)}")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f"Error removing sources: {e}")
        input("\nPress Enter to continue...")


def _handle_list_sources():
    """Handle listing all available sources with interactive detail view."""
    sources = get_available_sources()
    registry = get_source_registry()

    if not sources:
        print("\n  No sources available.")
        input("\n  Press Enter to continue...")
        return

    # Build sorted choice list with a Back option
    sorted_choices = sorted(sources.items(), key=lambda kv: kv[1])
    choices = [questionary.Choice(f"  {display_name}", sid) for sid, display_name in sorted_choices]
    choices.append(questionary.Separator())
    choices.append(questionary.Choice("Back to Source Management", "back"))

    while True:
        print_logo(menu_lines=len(choices) + 3)
        with suppress_logging():
            selected = questionary.select(
                "  Browse sources (select to view details):",
                choices=choices,
                style=custom_style,
                qmark="",
                pointer="▶",
                instruction="\n   (Use arrow keys, Enter to view details)",
            ).ask()

        if not selected or selected == 'back':
            return

        config = registry.get_source_config(selected)
        _show_source_detail(selected, config)


def _show_source_detail(source_id, config):
    """Display detailed information about a source and offer to edit article_count."""
    print("\n" + "─" * 70)
    print("\033[38;5;202m  Source Details\033[0m")
    print("─" * 70)

    if not config:
        print(f"\n  Source '{source_id}' not found in registry.")
        input("\n  Press Enter to continue...")
        return

    # Display core information
    print(f"\n  \033[1mID:\033[0m              {source_id}")
    print(f"  \033[1mName:\033[0m            {getattr(config, 'display_name', 'N/A')}")
    print(f"  \033[1mCategory:\033[0m        {getattr(config, 'category', 'N/A')}")
    print(f"  \033[1marticle_count:\033[0m   {getattr(config, 'article_count', 'N/A')}")

    if hasattr(config, 'base_url'):
        print(f"  \033[1mBase URL:\033[0m        {config.base_url}")

    if hasattr(config, 'discovery') and hasattr(config.discovery, 'method'):
        print(f"  \033[1mDiscovery:\033[0m       {config.discovery.method}")
        if config.discovery.method == 'rss' and hasattr(config.discovery, 'rss_urls'):
            rss_urls = config.discovery.rss_urls
            if hasattr(rss_urls, 'primary'):
                print(f"  \033[1mRSS Feed:\033[0m        {rss_urls.primary}")

    source_type = "Config-driven (YAML)" if hasattr(config, 'article_selectors') else "Custom (Python)"
    print(f"  \033[1mType:\033[0m            {source_type}")

    print("\n" + "─" * 70)

    with suppress_logging():
        action = questionary.select(
            "  Options:",
            choices=[
                questionary.Choice("Edit article count", "edit"),
                questionary.Choice("Back", "back"),
            ],
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n",
        ).ask()

    if action == "edit":
        _edit_source_count(source_id, config)


def _edit_source_count(source_id, config):
    """Prompt for a new article_count and write it to the userspace YAML."""
    from capcat.core.config import find_project_root, NoProjectError

    current_count = getattr(config, 'article_count', 30)

    while True:
        with suppress_logging():
            raw = questionary.text(
                f"  New article count (current: {current_count}):",
                default=str(current_count),
                style=custom_style,
                qmark="",
            ).ask()

        if raw is None:
            return

        try:
            new_count = int(raw.strip())
            if new_count <= 0:
                raise ValueError
            break
        except ValueError:
            print("  Invalid value — must be a positive integer.")

    try:
        project_root = find_project_root()
    except NoProjectError:
        print("  Could not locate project root. Cannot write config.")
        input("\n  Press Enter to continue...")
        return

    # Find userspace YAML path — config-driven sources
    yaml_file = (
        project_root
        / "Config"
        / "sources"
        / "active"
        / "config_driven"
        / "configs"
        / f"{source_id}.yaml"
    )

    if not yaml_file.exists():
        try:
            from capcat.core.source_config_mirror import SourceConfigMirror
            mirror = SourceConfigMirror(project_root)
            manifest = mirror._load_manifest()
            mirror._mirror_config_driven(manifest)
            mirror._save_manifest(manifest)
        except Exception as e:
            print(f"  Could not mirror source config: {e}")
            input("\n  Press Enter to continue...")
            return

    # Try custom source path if not found
    if not yaml_file.exists():
        custom_yaml = (
            project_root / "Config" / "sources" / "active" / "custom" / source_id / "config.yaml"
        )
        if custom_yaml.exists():
            yaml_file = custom_yaml

    if not yaml_file.exists():
        print(f"  Config file not found for '{source_id}'. Checked config-driven and custom paths.")
        input("\n  Press Enter to continue...")
        return

    existing_text = yaml_file.read_text(encoding="utf-8")
    lines = []
    found = False
    for line in existing_text.splitlines():
        if line.strip().startswith("article_count:"):
            lines.append(f"article_count: {new_count}  # Change the article count if needed")
            found = True
        else:
            lines.append(line)

    if not found:
        lines.append("")
        lines.append("# How many articles to fetch from this source per run. Change if needed.")
        lines.append(f"article_count: {new_count}")

    yaml_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n  article_count updated to {new_count} for '{source_id}'.")
    input("\n  Press Enter to continue...")


def _handle_test_source():
    """Handle testing a source."""
    from capcat.core.source_system.bundle_service import get_available_sources

    sources = get_available_sources()
    source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
    source_choices.append(questionary.Separator())
    source_choices.append(questionary.Choice("Back", "back"))

    print_logo(menu_lines=len(source_choices) + 3)
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
    from capcat.core.source_system.bundle_service import get_available_bundles, get_available_sources
    from capcat.core.source_system.source_registry import get_source_registry

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

    print_logo(menu_lines=len(bundle_choices) + 3)
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
    from capcat.core.source_system.bundle_service import get_available_sources
    sources = get_available_sources()

    source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
    source_choices.append(questionary.Separator())
    source_choices.append(questionary.Choice("Back to Main Menu", "back"))

    print_logo(menu_lines=len(source_choices) + 3)
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
    from capcat.core.source_system.bundle_service import get_available_sources
    sources = get_available_sources()

    source_choices = [questionary.Choice(name, sid) for sid, name in sources.items()]
    source_choices.append(questionary.Separator())
    source_choices.append(questionary.Choice("Back to Main Menu", "back"))

    print_logo(menu_lines=len(source_choices) + 3)
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
    print_logo(menu_lines=4)
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
    print_logo(menu_lines=8)
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
    from capcat.core.tui_context import is_tui_active, reset_fetch_results, get_fetch_result
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

    print(
        "\n  Note: Downloading PDFs can slow down the process significantly.\n"
        "  You can configure the PDF size limit and other behaviors in\n"
        "  Config/Global-settings.yaml inside your vault.\n"
    )
    with suppress_logging():
        want_pdfs = questionary.confirm(
            "  Download attached PDFs?",
            default=True,
            style=custom_style,
            qmark="",
        ).ask()
    if want_pdfs:
        args.append('--media')

    if is_tui_active():
        reset_fetch_results()

    success = True
    try:
        print("Executing command...")
        from capcat.cli import _dispatch
        _dispatch(args)
    except SystemExit as e:
        if e.code != 0:
            print(f"\nCommand finished with error code: {e.code}")
            success = False
        # code 0 = success, continue
    except Exception as e:
        print(f"\nError: {e}")
        success = False

    fetch_result = get_fetch_result() if is_tui_active() else None
    _show_completion_screen(generate_html, success, fetch_result=fetch_result)


def _show_completion_screen(generate_html: bool, success: bool, fetch_result=None) -> None:
    """Show post-execution screen with status, HTML link, and navigation choices.

    Args:
        generate_html: Whether HTML generation was requested.
        success: Whether the command completed without errors.
        fetch_result: Optional FetchResult with saved/skipped counts (TUI only).
    """
    print_logo()
    status_label = "Done" if success else "Completed with errors"
    print(f"\n  {status_label}")

    if fetch_result is not None:
        saved = fetch_result.saved
        total_skipped = sum(n for _, n in fetch_result.skipped)
        if saved > 0 or total_skipped > 0:
            if total_skipped == 0:
                print(f"\n  {saved} saved")
            else:
                parts = ", ".join(
                    f"{n} {r}" for r, n in fetch_result.skipped
                )
                print(f"\n  {saved} saved, {total_skipped} skipped ({parts})")

    if generate_html:
        html_path = _find_latest_index_html()
        if html_path:
            print(f"\n  HTML index: file://{html_path}")
        else:
            print("\n  HTML index: not found")

    print()

    with suppress_logging():
        choice = questionary.select(
            "  What would you like to do next?",
            choices=[
                questionary.Choice("Back to Main Menu", "menu"),
                questionary.Choice("Exit", "exit"),
            ],
            style=custom_style,
            qmark="",
            pointer="▶",
            instruction="\n   (Use arrow keys to navigate)",
        ).ask()

    if not choice or choice == "exit":
        print("Exiting interactive mode.")
        sys.exit(0)
    # choice == "menu": return, call stack unwinds to start_interactive_mode() while loop


def _find_latest_index_html() -> "str | None":
    """Find the most recently modified HTML output file.

    Checks both batch fetch index pages (News_*/index.html) and single
    article pages (Capcats/*/*/html/article.html), returning whichever
    was modified most recently.

    Returns:
        Absolute path string to the HTML file, or None if not found.
    """
    candidates: list[tuple[float, str]] = []
    try:
        from capcat.core.config import get_news_dir, get_capcats_dir

        # Batch fetches: News_*/index.html
        news_dir = get_news_dir()
        for date_dir in news_dir.glob("News_*"):
            index = date_dir / "index.html"
            if index.exists():
                candidates.append((index.stat().st_mtime, str(index.resolve())))

        # Single articles: Capcats/source_date/article/html/article.html
        capcats_dir = get_capcats_dir()
        for article_html in capcats_dir.glob("*/*/html/article.html"):
            candidates.append(
                (article_html.stat().st_mtime, str(article_html.resolve()))
            )
    except Exception:
        pass

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None


def _handle_manage_bundles():
    """Handle bundle management submenu."""
    from pathlib import Path
    from capcat.core.source_system.bundle_service import BundleService

    from capcat.core.config import find_project_root, NoProjectError
    try:
        project_root = find_project_root()
        user_path = project_root / "Config" / "sources" / "active" / "bundles" / "bundles.yml"
        bundles_path = user_path if user_path.exists() else (
            Path(__file__).parent.parent / "sources" / "builtin" / "bundles.yml"
        )
    except NoProjectError:
        bundles_path = Path(__file__).parent.parent / "sources" / "builtin" / "bundles.yml"
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
