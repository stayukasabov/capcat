#!/usr/bin/env python3
"""
Professional CLI interface for Capcat using subcommand architecture.
Follows industry standards like git, docker, and kubernetes.
"""

import argparse
import sys
import os
import re
import subprocess
from typing import List, Optional, Dict, Any
import questionary
from prompt_toolkit.styles import Style
from core.exceptions import ValidationError, CapcatError
from core.source_system.source_registry import get_source_registry
from core.logging_config import get_logger
import yaml
from pathlib import Path

# New imports for the add-source command
from core.source_system.rss_feed_introspector import RssFeedIntrospector
from core.source_system.source_config_generator import SourceConfigGenerator
from core.source_system.bundle_manager import BundleManager

# Imports for remove-source command
from core.source_system.remove_source_service import (
    create_remove_source_service
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


def get_available_sources() -> Dict[str, str]:
    """Get available sources from the source registry.

    Falls back to hardcoded sources if registry fails to load.

    Returns:
        Dictionary mapping source IDs to display names

    Raises:
        Exception: Caught and logged, triggers fallback sources
    """
    try:
        registry = get_source_registry()
        sources = {}

        for source_id in registry.get_available_sources():
            config = registry.get_source_config(source_id)
            if config:
                sources[source_id] = config.display_name

        return sources
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning(f"Failed to load sources from registry: {e}")
        return _get_fallback_sources()


def get_available_bundles() -> Dict[str, Dict[str, Any]]:
    """Get available bundles from bundles.yml file.

    Auto-populates 'all' bundle with all available sources from registry.
    Falls back to hardcoded bundles if file loading fails.

    Returns:
        Dictionary mapping bundle IDs to bundle data (sources, description)

    Raises:
        Exception: Caught and logged, triggers fallback bundles
    """
    try:
        bundles_file = (
            Path(__file__).parent / "sources" / "active" / "bundles.yml"
        )
        with open(bundles_file, 'r') as f:
            data = yaml.safe_load(f)
            bundles = {}
            for bundle_id, bundle_data in data.get('bundles', {}).items():
                bundles[bundle_id] = {
                    'sources': bundle_data.get('sources', []),
                    'description': bundle_data.get('description', '')
                }

            # Auto-populate 'all' bundle with all available
            # sources
            if 'all' in bundles:
                registry = get_source_registry()
                bundles['all']['sources'] = sorted(
                    registry.get_available_sources()
                )
                if not bundles['all']['description']:
                    bundles['all']['description'] = 'All available sources'

            return bundles
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning(f"Failed to load bundles from bundles.yml: {e}")
        return _get_fallback_bundles()


def _get_fallback_sources() -> Dict[str, str]:
    """Fallback source definitions if registry fails.

    Provides minimal set of core sources for basic functionality.

    Returns:
        Dictionary of hardcoded source IDs to display names
    """
    return {
        'hn': 'Hacker News',
        'lb': 'Lobsters',
        'iq': 'InfoQ',
        'bbc': 'BBC News',
        'nature': 'Nature',
    }


def _get_fallback_bundles() -> Dict[str, Dict[str, Any]]:
    """Fallback bundle definitions if registry fails.

    Provides minimal set of core bundles for basic functionality.

    Returns:
        Dictionary of hardcoded bundle IDs to bundle data
    """
    return {
        'tech': {
            'sources': ['hn', 'lb', 'iq'],
            'description': 'Tech news'
        },
        'news': {
            'sources': ['bbc'],
            'description': 'General news'
        },
        'science': {
            'sources': ['nature'],
            'description': 'Science news'
        },
        'all': {
            'sources': ['hn', 'lb', 'iq', 'bbc', 'nature'],
            'description': 'All sources'
        }
    }


# Dynamic source and bundle loading
AVAILABLE_SOURCES = get_available_sources()
BUNDLES = get_available_bundles()

# --- New functions for add-source command ---

def run_capcat_fetch(source_id: str, count: int) -> bool:
    """Run the './capcat fetch' command as a subprocess for testing new source.

    Designed to be easily mockable in tests.

    Args:
        source_id: Source identifier to test
        count: Number of articles to fetch

    Returns:
        True if fetch successful, False otherwise

    Raises:
        subprocess.CalledProcessError: If fetch command fails
    """
    command = ["./capcat", "fetch", source_id, "--count", str(count)]
    try:
        # Using subprocess.run to wait for completion and check the result
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # Raises CalledProcessError for non-zero exit codes
        )
        print(f"Test fetch successful for source '{source_id}'.")
        print(result.stdout)
        return True
    except FileNotFoundError:
        print(
            "Error: The 'capcat' command is not found. "
            "Make sure it's in your PATH or current directory."
        )
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error during test fetch for source '{source_id}':")
        print(e.stderr)
        return False

def add_source(url: str) -> None:
    """Interactive command to add a new RSS-based source.

    Guides user through: RSS inspection, configuration, bundle assignment,
    and test fetch. Creates YAML config in sources/active/config_driven/configs/.

    Args:
        url: RSS feed URL to add as new source

    Raises:
        SystemExit: If user cancels or configuration fails
    """
    print(f"\nAttempting to add new source from: {url}")

    try:
        # 1. Introspect the RSS feed
        print("Inspecting RSS feed...")
        introspector = RssFeedIntrospector(url)
        print(f"✓ Feed '{introspector.feed_title}' found.")

        # 2. Interactive Configuration
        print("\n--- Configure New Source ---")

        # Suggest a source ID
        suggested_id = re.sub(
            r'[^a-z0-9]', '', introspector.feed_title.lower()
        )
        source_id = questionary.text(
            "  Source ID (alphanumeric):",
            default=suggested_id,
            style=custom_style,
            qmark=""
        ).ask()
        if not source_id:
            print("Source ID cannot be empty. Aborting.")
            sys.exit(1)

        # Ask for category
        try:
            registry = get_source_registry()
            all_configs = [
                registry.get_source_config(sid)
                for sid in registry.get_available_sources()
            ]
            existing_categories = sorted(list(set(
                config.category for config in all_configs
                if config and hasattr(config, 'category')
            )))
        except Exception:
            existing_categories = []

        # fallback
        if not existing_categories:
            existing_categories = [
                'tech', 'news', 'science', 'ai', 'sports', 'general'
            ]

        category = questionary.select(
            "  Select category:",
            choices=existing_categories,
            use_indicator=True,
            style=custom_style,
            qmark="",
            pointer="▶"
        ).ask()
        if not category:
            print("Category selection cancelled. Aborting.")
            sys.exit(1)

        # 3. Generate Config
        source_metadata = {
            "source_id": source_id,
            "display_name": introspector.feed_title,
            "base_url": introspector.base_url,
            "rss_url": introspector.url,
            "category": category
        }
        config_generator = SourceConfigGenerator(source_metadata)
        config_path = (
            Path(__file__).parent / "sources" / "active" /
            "config_driven" / "configs"
        )
        saved_path = config_generator.generate_and_save(
            str(config_path)
        )
        print(f"✓ Configuration file created at: {saved_path}")

        # 4. Add to Bundle (Optional)
        if questionary.confirm(
            "  Add to bundle?",
            style=custom_style,
            qmark=""
        ).ask():
            bundles_path = str(
                Path(__file__).parent / "sources" / "active" /
                "bundles.yml"
            )
            bundle_manager = BundleManager(bundles_path)
            bundle_to_add = questionary.select(
                "  Select bundle:",
                choices=bundle_manager.get_bundle_names(),
                use_indicator=True,
                style=custom_style,
                qmark="",
                pointer="▶"
            ).ask()
            if bundle_to_add:
                bundle_manager.add_source_to_bundle(
                    source_id, bundle_to_add
                )
                print(
                    f"✓ Added '{source_id}' to bundle "
                    f"'{bundle_to_add}'."
                )

        # 5. Automated Test
        if questionary.confirm(
            "  Test fetch? (recommended)",
            style=custom_style,
            qmark=""
        ).ask():
            print("\n--- Running Test Fetch ---")
            if not run_capcat_fetch(source_id, 1):
                print(
                    "\nTest fetch failed. The source might need "
                    "manual adjustments."
                )
                print(f"Check the generated file: {saved_path}")
            else:
                print("\n✓ Source added and verified successfully!")

    except CapcatError as e:
        print(f"Error: {e.user_message}", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, TypeError):
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)


def remove_source(args: argparse.Namespace) -> None:
    """Enhanced command to remove existing sources with advanced options.

    Supports dry-run, backup, analytics, batch removal, and undo operations.

    Args:
        args: Parsed command-line arguments with removal options

    Raises:
        CapcatError: If source removal fails
        SystemExit: If user cancels operation
    """
    # Handle undo mode
    if hasattr(args, 'undo') and args.undo is not None:
        _handle_undo(args.undo)
        return

    # Standard removal mode
    print("\n--- Remove Source ---")

    try:
        from core.source_system.enhanced_remove_command import (
            EnhancedRemoveCommand,
            RemovalOptions
        )
        from core.source_system.source_backup_manager import (
            SourceBackupManager
        )
        from core.source_system.source_analytics import SourceAnalytics
        from pathlib import Path

        # Create service components
        service = create_remove_source_service()
        backup_manager = SourceBackupManager()
        analytics = SourceAnalytics()

        # Build removal options
        options = RemovalOptions(
            dry_run=getattr(args, 'dry_run', False),
            create_backup=not getattr(args, 'no_backup', False),
            show_analytics=not getattr(args, 'no_analytics', False),
            batch_file=(Path(args.batch) if hasattr(args, 'batch')
                        and args.batch else None),
            force=getattr(args, 'force', False)
        )

        # Get base command from service
        base_command = service._create_remove_source_command()

        # Create enhanced command
        from core.source_system.removal_ui import QuestionaryRemovalUI
        enhanced_command = EnhancedRemoveCommand(
            base_command=base_command,
            backup_manager=backup_manager,
            analytics=analytics,
            ui=QuestionaryRemovalUI(),
            logger=get_logger(__name__)
        )

        # Execute with options
        enhanced_command.execute_with_options(options)

    except CapcatError as e:
        print(f"Error: {e.user_message}", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, TypeError):
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)


def _handle_undo(backup_id: str) -> None:
    """Handle undo/restore operation.

    Restores sources from backup using specified backup ID.

    Args:
        backup_id: Backup identifier to restore from

    Raises:
        CapcatError: If restore operation fails
    """
    print("\n--- Restore Sources from Backup ---")

    try:
        from core.source_system.enhanced_remove_command import (
            EnhancedRemoveCommand
        )
        from core.source_system.source_backup_manager import (
            SourceBackupManager
        )
        from core.source_system.source_analytics import SourceAnalytics
        from core.source_system.removal_ui import QuestionaryRemovalUI

        service = create_remove_source_service()
        base_command = service._create_remove_source_command()

        enhanced_command = EnhancedRemoveCommand(
            base_command=base_command,
            backup_manager=SourceBackupManager(),
            analytics=SourceAnalytics(),
            ui=QuestionaryRemovalUI(),
            logger=get_logger(__name__)
        )

        # Use 'latest' or specific backup ID
        if backup_id == 'latest':
            enhanced_command.execute_undo(None)  # Will select most recent
        else:
            enhanced_command.execute_undo(backup_id)

    except CapcatError as e:
        print(f"Error: {e.user_message}", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, TypeError):
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)


def generate_config_command(args: argparse.Namespace) -> None:
    """Launch the interactive config generator script.

    Executes scripts/generate_source_config.py as subprocess.

    Args:
        args: Parsed command-line arguments with optional output path

    Raises:
        SystemExit: If script not found or execution fails
    """
    try:
        import subprocess
        from pathlib import Path

        # Path to the config generator script
        script_path = (
            Path(__file__).parent / "scripts" /
            "generate_source_config.py"
        )

        if not script_path.exists():
            print(
                f"Error: Config generator script not found at "
                f"{script_path}", file=sys.stderr
            )
            sys.exit(1)

        # Build command
        cmd = [sys.executable, str(script_path)]

        # Pass output path if specified
        if hasattr(args, 'output') and args.output:
            cmd.extend(['--output', args.output])

        # Run the script
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)

    except Exception as e:
        print(f"Error running config generator: {e}", file=sys.stderr)
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands.

    Defines global options and all subcommands (single, fetch, bundle, catch,
    add-source, remove-source, generate-config, list).

    Returns:
        Configured ArgumentParser instance
    """
    
    parser = argparse.ArgumentParser(
        prog='capcat',
        description='Capcat v2.0 - News Article Scanner & Archiver',
        epilog="""
Examples:
  # Quick start - fetch tech news
  capcat bundle tech --count 10

  # Download single article
  capcat single https://news.ycombinator.com/item?id=12345

  # See available sources
  capcat list sources

  # Interactive mode (easiest for beginners)
  capcat catch

  # Get help on any command
  capcat <command> --help

For detailed help on any subcommand: capcat <command> --help
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        '--version', '-v', action='version', version='Capcat v2.0.0'
    )
    parser.add_argument(
        '--verbose', '-V', action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Show only warnings and errors'
    )
    parser.add_argument(
        '--config', '-C', metavar='FILE',
        help='Configuration file path'
    )
    parser.add_argument(
        '--log-file', '-L', metavar='FILE',
        help='Write detailed logs to file'
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest='command', title='Commands',
        help='Command to execute', metavar='<command>'
    )

    # Single article command
    single_parser = subparsers.add_parser(
        'single', help='Download a single article from URL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download single article
  capcat single https://news.ycombinator.com/item?id=12345

  # Download with HTML generation
  capcat single https://bbc.com/news/technology-12345 --html

  # Download all media (images, videos, documents)
  capcat single https://nature.com/articles/12345 --media

  # Save to custom directory
  capcat single URL --output ~/Articles

  # Download with verbose logging to file
  capcat single URL --verbose --log-file download.log

  # Update previously downloaded article
  capcat single URL --update
        """
    )
    single_parser.add_argument('url', help='Article URL to download')
    single_parser.add_argument(
        '--output', '-o', metavar='DIR', default='.',
        help='Output directory'
    )
    single_parser.add_argument(
        '--media', '-M', action='store_true',
        help='Download all media files'
    )
    single_parser.add_argument(
        '--html', '-H', action='store_true',
        help='Generate HTML files'
    )
    single_parser.add_argument(
        '--update', '-U', action='store_true',
        help='Update existing article'
    )

    # Fetch command
    fetch_parser = subparsers.add_parser(
        'fetch', help='Fetch articles from specific sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch from single source (use './capcat list sources' to see all)
  capcat fetch hn

  # Fetch specific number of articles
  capcat fetch hn --count 10

  # Fetch from multiple sources
  capcat fetch hn,bbc,nature --count 15

  # Fetch with HTML generation
  capcat fetch hn,lb --html

  # Fetch all media types
  capcat fetch bbc --media --count 5

  # Save to custom directory
  capcat fetch hn --output ~/News --count 20

  # Fetch with verbose output and logging
  capcat fetch hn,bbc --verbose --log-file fetch.log
        """
    )
    fetch_parser.add_argument(
        'sources', nargs='?', help='Comma-separated sources'
    )
    fetch_parser.add_argument(
        '--count', '-c', type=int, default=30, metavar='N',
        help='Number of articles per source'
    )
    fetch_parser.add_argument(
        '--output', '-o', metavar='DIR', default='.',
        help='Output directory'
    )
    fetch_parser.add_argument(
        '--media', '-M', action='store_true',
        help='Download all media files'
    )
    fetch_parser.add_argument(
        '--html', '-H', action='store_true',
        help='Generate HTML files'
    )
    fetch_parser.add_argument(
        '--update', '-U', action='store_true',
        help='Update existing articles'
    )

    # Bundle command
    bundle_parser = subparsers.add_parser(
        'bundle', help='Fetch articles from predefined source bundles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch tech news bundle (use './capcat list bundles' to see all)
  capcat bundle tech

  # Fetch specific number from bundle
  capcat bundle tech --count 10

  # Fetch news bundle with HTML
  capcat bundle news --html

  # Fetch science articles with all media
  capcat bundle science --media --count 5

  # Fetch all available bundles
  capcat bundle --all

  # Save to custom directory
  capcat bundle tech --output ~/TechNews

  # Verbose mode with logging
  capcat bundle tech --verbose --log-file bundle.log --count 15
        """
    )
    bundle_parser.add_argument(
        'bundle', nargs='?', choices=list(BUNDLES.keys()),
        help='Bundle name to fetch'
    )
    bundle_parser.add_argument(
        '--count', '-c', type=int, default=30, metavar='N',
        help='Number of articles per source'
    )
    bundle_parser.add_argument(
        '--output', '-o', metavar='DIR', default='.',
        help='Output directory'
    )
    bundle_parser.add_argument(
        '--media', '-M', action='store_true',
        help='Download all media files'
    )
    bundle_parser.add_argument(
        '--html', '-H', action='store_true',
        help='Generate HTML files'
    )
    bundle_parser.add_argument(
        '--all', '-A', action='store_true',
        help='Activate all available bundles'
    )
    bundle_parser.add_argument(
        '--update', '-U', action='store_true',
        help='Update existing bundle articles'
    )

    # List command
    list_parser = subparsers.add_parser(
        'list', help='List available sources and bundles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available sources grouped by category
  capcat list sources

  # List available bundles
  capcat list bundles

  # List both sources and bundles
  capcat list
  capcat list all
        """
    )
    list_parser.add_argument(
        'what', nargs='?',
        choices=['sources', 'bundles', 'all'], default='all',
        help='What to list'
    )

    # Config command
    config_parser = subparsers.add_parser(
        'config', help='Configuration management'
    )
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument(
        '--show', '-s', action='store_true',
        help='Show current configuration'
    )
    config_group.add_argument(
        '--set', metavar='KEY=VALUE',
        help='Set configuration value'
    )

    # Add-source command
    add_source_parser = subparsers.add_parser(
        'add-source', help='Add a new RSS source interactively',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_source_parser.add_argument(
        '--url', required=True, help='URL of the RSS feed to add'
    )

    # Remove-source command
    remove_source_parser = subparsers.add_parser(
        'remove-source',
        help='Remove existing sources interactively',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  capcat remove-source                    Interactive removal
  capcat remove-source --dry-run          Preview changes without removing
  capcat remove-source --batch sources.txt  Remove sources from file
  capcat remove-source --undo             Restore last removal
  capcat remove-source --undo backup_123  Restore specific backup
  capcat remove-source --no-backup        Skip creating backup
  capcat remove-source --no-analytics     Skip usage statistics
        """
    )
    remove_source_parser.add_argument(
        '--dry-run', '-n', action='store_true',
        help='Preview changes without removing anything'
    )
    remove_source_parser.add_argument(
        '--batch', '-b', metavar='FILE',
        help='Remove sources listed in file (one per line)'
    )
    remove_source_parser.add_argument(
        '--undo', '-u', nargs='?', const='latest', metavar='BACKUP_ID',
        help='Restore sources from backup'
    )
    remove_source_parser.add_argument(
        '--no-backup', action='store_true',
        help='Skip creating backup before removal'
    )
    remove_source_parser.add_argument(
        '--no-analytics', action='store_true',
        help='Skip showing usage analytics'
    )
    remove_source_parser.add_argument(
        '--force', '-f', action='store_true',
        help='Skip confirmation prompts'
    )

    # Generate-config command
    generate_config_parser = subparsers.add_parser(
        'generate-config',
        help='Generate comprehensive YAML configuration for new sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  capcat generate-config
      Interactive config generation
  capcat generate-config --output custom.yaml
      Save to custom location
        """
    )
    generate_config_parser.add_argument(
        '--output', '-o', metavar='FILE',
        help='Output file path '
             '(default: sources/active/config_driven/configs/)'
    )

    # Catch command
    subparsers.add_parser('catch', help='Start interactive mode')
    
    return parser

def parse_sources(sources_str: str) -> List[str]:
    """Parse comma-separated sources string and validate.

    Args:
        sources_str: Comma-separated source identifiers

    Returns:
        List of validated source IDs

    Raises:
        ValidationError: If any source ID is unknown
    """
    sources = [s.strip() for s in sources_str.split(',')]
    invalid_sources = [
        s for s in sources if s not in AVAILABLE_SOURCES
    ]
    if invalid_sources:
        raise ValidationError(
            "sources", ','.join(invalid_sources),
            f"Unknown sources. Available: "
            f"{', '.join(sorted(AVAILABLE_SOURCES.keys()))}"
        )
    return sources

def validate_arguments(args: argparse.Namespace) -> Dict[str, Any]:
    """Validate and process parsed arguments.

    Converts argparse Namespace to configuration dictionary for capcat.py.
    Handles all subcommands and validates required arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configuration dictionary with action, sources, options

    Raises:
        ValidationError: If required arguments missing or invalid
    """
    if not args.command:
        return {'action': 'help'}
    
    # Base config for all commands
    config = {
        'action': args.command,
        'verbose': getattr(args, 'verbose', False),
        'quiet': getattr(args, 'quiet', False),
        'log_file': getattr(args, 'log_file', None)
    }

    if args.command == 'single':
        config.update({
            'url': args.url,
            'output': args.output,
            'media': args.media,
            'update': getattr(args, 'update', False),
            'html': getattr(args, 'html', False),
        })
    elif args.command == 'fetch':
        if not args.sources:
            raise ValidationError(
                "sources", "",
                "Must provide a comma-separated list of sources."
            )
        config.update({
            'sources': parse_sources(args.sources),
            'count': args.count,
            'output': args.output,
            'media': args.media,
            'html': getattr(args, 'html', False),
            'update': getattr(args, 'update', False),
        })
    elif args.command == 'bundle':
        # Handle --all flag
        if getattr(args, 'all', False):
            ordered_bundles = [
                'techpro', 'tech', 'news', 'science', 'ai'
            ]
            active_bundles = []
            for bundle_name in ordered_bundles:
                if bundle_name in BUNDLES and BUNDLES[bundle_name]:
                    active_bundles.append(bundle_name)
            bundle_name_str = (
                f"all-bundles-ordered({', '.join(active_bundles)})"
            )
            sources = active_bundles
        else:
            if not args.bundle:
                raise ValidationError(
                    "bundle", "missing",
                    "bundle name is required when --all is not used"
                )
            sources = BUNDLES[args.bundle]['sources']
            bundle_name_str = args.bundle

        config.update({
            'sources': sources,
            'count': args.count,
            'output': args.output,
            'media': args.media,
            'html': getattr(args, 'html', False),
            'update': getattr(args, 'update', False),
            'bundle_name': bundle_name_str,
            'all_bundles': getattr(args, 'all', False),
        })
    elif args.command in [
        'list', 'config', 'catch', 'add-source', 'remove-source'
    ]:
        # These commands are handled directly or have simple args
        if args.command == 'add-source':
            config['url'] = args.url
        if args.command == 'list':
            config['what'] = args.what
    else:
        raise ValidationError("command", args.command, "Unknown command")
        
    return config

def list_sources_and_bundles(what: str = 'all') -> None:
    """Display available sources and bundles.

    Args:
        what: What to list - 'sources', 'bundles', or 'all'
    """
    sources = get_available_sources()
    registry = get_source_registry()

    if what in ['sources', 'all']:
        # Group by category
        categories = {}
        for source_id, display_name in sorted(sources.items()):
            try:
                config = registry.get_source_config(source_id)
                category = config.category.upper() if config and hasattr(config, 'category') else 'OTHER'
            except:
                category = 'OTHER'

            if category not in categories:
                categories[category] = []
            categories[category].append((source_id, display_name))

        # Print formatted output
        print("\n--- Available Sources ---\n")
        for category, source_list in sorted(categories.items()):
            print(f"{category}:")
            for source_id, display_name in source_list:
                print(f"  - {source_id:15} {display_name}")
            print()  # Blank line between categories

        print(f"Total: {len(sources)} sources\n")

    if what in ['bundles', 'all']:
        bundles = get_available_bundles()

        print("\n--- Available Bundles ---\n")
        for bundle_id, bundle_data in sorted(bundles.items()):
            sources_str = ", ".join(bundle_data['sources'][:3])
            if len(bundle_data['sources']) > 3:
                sources_str += f", ... ({len(bundle_data['sources'])} total)"
            desc = bundle_data.get('description', '')
            print(f"{bundle_id}: {desc}")
            print(f"  Sources: {sources_str}")
            print()

def parse_arguments(argv: Optional[List[str]] = None) -> Dict[str, Any]:
    """Parse command line arguments and return validated configuration.

    Handles immediate-exit commands (list, add-source, remove-source,
    generate-config, catch) and validates remaining commands.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Validated configuration dictionary

    Raises:
        ValidationError: If arguments invalid
        SystemExit: For immediate-exit commands
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Handle commands that exit immediately
    if args.command == 'list':
        list_sources_and_bundles(args.what)
        sys.exit(0)
    elif args.command == 'add-source':
        add_source(args.url)
        sys.exit(0)
    elif args.command == 'remove-source':
        remove_source(args)
        sys.exit(0)
    elif args.command == 'generate-config':
        generate_config_command(args)
        sys.exit(0)
    elif args.command == 'config':
        # ... (config logic)
        print("Config command not yet implemented.")
        sys.exit(0)

    try:
        return validate_arguments(args)
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for direct CLI script execution.

    Parses arguments and executes commands. Used when cli.py run directly.
    Normal usage goes through capcat.py which imports functions from here.
    """
    config = parse_arguments()
    if config:
        print(f"Running command '{config['action']}' with config: {config}")

if __name__ == '__main__':
    main()