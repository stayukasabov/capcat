#!/usr/bin/env python3
"""
Enhanced CLI validation and error handling for better user experience.
"""

import sys
from typing import List, Dict, Any, Optional
from difflib import get_close_matches


class CLIValidationError(Exception):
    """Custom exception for CLI validation errors."""
    pass


class CLIValidator:
    """Enhanced CLI validation with helpful error messages."""

    def __init__(self):
        self.common_flag_mistakes = {
            # Common mistakes mapping to correct flags
            '-html': '--html or -H',
            '-verbose': '--verbose or -V',
            '-count': '--count or -c',
            '-media': '--media or -M',
            '-output': '--output or -o',
            '-update': '--update or -U',
            '-quiet': '--quiet or -q',
            '-help': '--help or -h',
            # Single letter mistakes
            '-v': '--verbose (note: -v is --version)',
            '-h': '--help (triggered help display)',
        }

    def validate_unknown_args(self, unknown_args: List[str], valid_flags: List[str]) -> None:
        """
        Validate unknown arguments and provide helpful suggestions.

        Args:
            unknown_args: List of unrecognized arguments
            valid_flags: List of valid flag names

        Raises:
            CLIValidationError: If invalid flags are found with suggestions
        """
        if not unknown_args:
            return

        errors = []

        for arg in unknown_args:
            if arg.startswith('-'):
                # Check for common mistakes
                if arg in self.common_flag_mistakes:
                    errors.append(f"Invalid flag '{arg}' - did you mean {self.common_flag_mistakes[arg]}?")
                else:
                    # Use fuzzy matching to find close matches
                    close_matches = get_close_matches(arg, valid_flags, n=2, cutoff=0.6)
                    if close_matches:
                        suggestions = ', '.join(close_matches)
                        errors.append(f"Invalid flag '{arg}' - did you mean: {suggestions}?")
                    else:
                        errors.append(f"Invalid flag '{arg}' - see --help for available options")

        if errors:
            error_msg = "Command line errors found:\n" + "\n".join(f"  • {err}" for err in errors)
            raise CLIValidationError(error_msg)

    def detect_flag_typos(self, args_string: str) -> List[str]:
        """
        Detect common flag typing mistakes in command string.

        Args:
            args_string: Full command line arguments as string

        Returns:
            List of detected issues with suggestions
        """
        issues = []

        # Check for single dash with long names
        import re
        single_dash_long = re.findall(r'\s(-[a-zA-Z]{2,})', args_string)
        for match in single_dash_long:
            if match in self.common_flag_mistakes:
                issues.append(f"Found '{match}' - use {self.common_flag_mistakes[match]} instead")
            else:
                issues.append(f"Found '{match}' - long flags need double dash (--)")

        return issues

    def suggest_correct_command(self, original_command: str) -> Optional[str]:
        """
        Suggest corrected command based on common mistakes.

        Args:
            original_command: Original command with errors

        Returns:
            Suggested corrected command or None
        """
        corrected = original_command

        # Apply common corrections
        corrections = {
            ' -html': ' --html',
            ' -verbose': ' --verbose',
            ' -count': ' --count',
            ' -media': ' --media',
            ' -output': ' --output',
            ' -update': ' --update',
            ' -quiet': ' --quiet',
        }

        for mistake, correction in corrections.items():
            if mistake in corrected:
                corrected = corrected.replace(mistake, correction)

        return corrected if corrected != original_command else None


def validate_cli_args(args: Any, command_line: str) -> None:
    """
    Validate CLI arguments and provide helpful error messages.

    Args:
        args: Parsed arguments object
        command_line: Original command line string

    Raises:
        CLIValidationError: If validation fails
    """
    validator = CLIValidator()

    # Check for common flag typos in original command
    issues = validator.detect_flag_typos(command_line)

    if issues:
        suggestion = validator.suggest_correct_command(command_line)

        error_msg = "Command contains flag errors:\n"
        error_msg += "\n".join(f"  • {issue}" for issue in issues)

        if suggestion:
            error_msg += f"\n\nDid you mean:\n  {suggestion}"

        error_msg += f"\n\nRun 'capcat {args.command} --help' for correct syntax"

        raise CLIValidationError(error_msg)


# Decorator for CLI commands
def with_cli_validation(func):
    """Decorator to add CLI validation to command functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CLIValidationError as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
    return wrapper