#!/usr/bin/env python3
"""
CLI error recovery and user guidance system.
"""

import sys
from typing import List, Dict, Optional, Tuple
from core.cli_validation import CLIValidator


class CLIRecovery:
    """System for recovering from CLI errors and guiding users."""

    def __init__(self):
        self.validator = CLIValidator()

    def handle_help_triggered_by_error(self, args: List[str]) -> bool:
        """
        Handle cases where help was triggered by a syntax error.

        Args:
            args: Command line arguments

        Returns:
            True if error was detected and handled, False otherwise
        """
        # Check if help was likely triggered by a flag mistake
        suspicious_flags = [arg for arg in args if self._is_suspicious_flag(arg)]

        if suspicious_flags:
            print("\n🔍 It looks like help was displayed due to a flag syntax error!", file=sys.stderr)
            print("\nDetected issues:", file=sys.stderr)

            for flag in suspicious_flags:
                suggestion = self._get_flag_suggestion(flag)
                if suggestion:
                    print(f"  • '{flag}' should be '{suggestion}'", file=sys.stderr)

            self._show_recovery_options(args)
            return True

        return False

    def _is_suspicious_flag(self, arg: str) -> bool:
        """Check if argument looks like a common flag mistake."""
        suspicious_patterns = [
            '-html', '-verbose', '-count', '-media', '-output', '-update', '-quiet'
        ]
        return arg in suspicious_patterns

    def _get_flag_suggestion(self, flag: str) -> Optional[str]:
        """Get suggested correction for a flag."""
        corrections = {
            '-html': '--html',
            '-verbose': '--verbose',
            '-count': '--count',
            '-media': '--media',
            '-output': '--output',
            '-update': '--update',
            '-quiet': '--quiet'
        }
        return corrections.get(flag)

    def _show_recovery_options(self, args: List[str]):
        """Show recovery options to the user."""
        original_command = ' '.join(['capcat'] + args)
        corrected = self._auto_correct_command(original_command)

        if corrected and corrected != original_command:
            print(f"\nSuggested correction:", file=sys.stderr)
            print(f"  {corrected}", file=sys.stderr)

        print("\nQuick reference for common flags:", file=sys.stderr)
        print("  --html or -H     Generate HTML files", file=sys.stderr)
        print("  --verbose or -V  Enable verbose output", file=sys.stderr)
        print("  --count N or -c N   Number of articles", file=sys.stderr)
        print("  --media or -M    Download media files", file=sys.stderr)
        print("  --help or -h     Show help", file=sys.stderr)

    def _auto_correct_command(self, command: str) -> str:
        """Automatically correct common command mistakes."""
        corrections = {
            ' -html': ' --html',
            ' -verbose': ' --verbose',
            ' -count': ' --count',
            ' -media': ' --media',
            ' -output': ' --output',
            ' -update': ' --update',
            ' -quiet': ' --quiet'
        }

        corrected = command
        for mistake, correction in corrections.items():
            corrected = corrected.replace(mistake, correction)

        return corrected

    def suggest_alternative_commands(self, failed_command: str, command_type: str) -> List[str]:
        """
        Suggest alternative commands when the current one fails.

        Args:
            failed_command: The command that failed
            command_type: Type of command ('fetch', 'bundle', etc.)

        Returns:
            List of suggested alternative commands
        """
        suggestions = []

        if command_type == 'fetch':
            suggestions.extend([
                "capcat fetch hn --html",
                "capcat fetch hn --count 10",
                "capcat fetch hn --verbose",
                "capcat list sources  # See available sources"
            ])

        elif command_type == 'bundle':
            suggestions.extend([
                "capcat bundle tech --html",
                "capcat bundle news --count 15",
                "capcat list bundles  # See available bundles"
            ])

        elif command_type == 'single':
            suggestions.extend([
                "capcat single https://example.com/article --html",
                "capcat single URL --media"
            ])

        return suggestions

    def provide_contextual_help(self, command_type: str, error_context: Dict):
        """
        Provide contextual help based on the specific error and command type.

        Args:
            command_type: Type of command that failed
            error_context: Context about what went wrong
        """
        print(f"\n💡 Help for '{command_type}' command:", file=sys.stderr)

        if command_type == 'fetch':
            print("  Purpose: Download articles from news sources", file=sys.stderr)
            print("  Format:  capcat fetch <sources> [options]", file=sys.stderr)
            print("  Example: capcat fetch hn --html --count 10", file=sys.stderr)

        elif command_type == 'bundle':
            print("  Purpose: Download articles from predefined source bundles", file=sys.stderr)
            print("  Format:  capcat bundle <bundle_name> [options]", file=sys.stderr)
            print("  Example: capcat bundle tech --html --count 15", file=sys.stderr)

        elif command_type == 'single':
            print("  Purpose: Download a single article from URL", file=sys.stderr)
            print("  Format:  capcat single <URL> [options]", file=sys.stderr)
            print("  Example: capcat single https://example.com/article --html", file=sys.stderr)

        print(f"\n  Run 'capcat {command_type} --help' for detailed options", file=sys.stderr)


def handle_cli_error_recovery(args: List[str], command_type: Optional[str] = None) -> bool:
    """
    Handle CLI error recovery and provide user guidance.

    Args:
        args: Command line arguments that caused error
        command_type: Type of command if known

    Returns:
        True if recovery guidance was provided
    """
    recovery = CLIRecovery()

    # Try to handle help triggered by error
    if recovery.handle_help_triggered_by_error(args):
        return True

    # Provide contextual help if command type is known
    if command_type:
        recovery.provide_contextual_help(command_type, {"args": args})
        return True

    return False