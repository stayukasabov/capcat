#!/usr/bin/env python3
"""
Enhanced ArgumentParser with better error messages and validation.
"""

import argparse
import sys
from typing import List, Optional
from core.cli_validation import CLIValidator


class EnhancedArgumentParser(argparse.ArgumentParser):
    """
    Enhanced ArgumentParser with improved error messages and validation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = CLIValidator()
        self._original_command = None

    def parse_args(self, args: Optional[List[str]] = None, namespace=None):
        """Enhanced parse_args with better error handling."""
        if args is None:
            args = sys.argv[1:]

        # Store original command for error reporting
        self._original_command = ' '.join(['capcat'] + args)

        try:
            # First try normal parsing
            parsed_args = super().parse_args(args, namespace)
            return parsed_args

        except SystemExit as e:
            # Catch help display or parsing errors
            if e.code == 0:
                # Help was displayed, check if it was triggered by mistake
                if args and any('-html' in arg or '-verbose' in arg or
                              any(f'-{flag}' in arg for flag in ['count', 'media', 'output', 'update'])
                              for arg in args):
                    self._handle_flag_mistakes(args)
                # Re-raise to maintain help behavior
                raise
            else:
                # Parsing error occurred
                self._handle_parsing_error(args, e)
                raise

    def _handle_flag_mistakes(self, args: List[str]):
        """Handle common flag mistakes that trigger help."""
        print("\n⚠️  It looks like you may have a flag syntax error!", file=sys.stderr)

        issues = self.validator.detect_flag_typos(' '.join(args))
        if issues:
            print("\nDetected issues:", file=sys.stderr)
            for issue in issues:
                print(f"  • {issue}", file=sys.stderr)

            suggestion = self.validator.suggest_correct_command(self._original_command)
            if suggestion:
                print(f"\nDid you mean:", file=sys.stderr)
                print(f"  {suggestion}", file=sys.stderr)

        print("\nCommon flag formats:", file=sys.stderr)
        print("  --html  (not -html)", file=sys.stderr)
        print("  --verbose  (not -verbose)", file=sys.stderr)
        print("  --count 10  (not -count 10)", file=sys.stderr)

    def _handle_parsing_error(self, args: List[str], error: SystemExit):
        """Handle parsing errors with enhanced messages."""
        print(f"\n❌ Command parsing failed", file=sys.stderr)

        # Check for flag issues
        issues = self.validator.detect_flag_typos(' '.join(args))
        if issues:
            print("\nPossible issues:", file=sys.stderr)
            for issue in issues:
                print(f"  • {issue}", file=sys.stderr)

            suggestion = self.validator.suggest_correct_command(self._original_command)
            if suggestion:
                print(f"\nSuggested fix:", file=sys.stderr)
                print(f"  {suggestion}", file=sys.stderr)

    def error(self, message):
        """Override error method to provide enhanced error messages."""
        # Check if this is a flag-related error
        if any(word in message.lower() for word in ['unrecognized', 'invalid', 'unknown']):
            print(f"\n❌ {message}", file=sys.stderr)

            if self._original_command:
                issues = self.validator.detect_flag_typos(self._original_command)
                if issues:
                    print("\nDetected flag issues:", file=sys.stderr)
                    for issue in issues:
                        print(f"  • {issue}", file=sys.stderr)

                    suggestion = self.validator.suggest_correct_command(self._original_command)
                    if suggestion:
                        print(f"\nDid you mean:", file=sys.stderr)
                        print(f"  {suggestion}", file=sys.stderr)

            print(f"\nUse 'capcat --help' or 'capcat <command> --help' for usage information", file=sys.stderr)
            sys.exit(2)
        else:
            # Fall back to standard error handling
            super().error(message)


def create_enhanced_parser(*args, **kwargs) -> EnhancedArgumentParser:
    """Create an enhanced argument parser with better error messages."""
    return EnhancedArgumentParser(*args, **kwargs)