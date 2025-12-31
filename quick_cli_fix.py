#!/usr/bin/env python3
"""
Quick CLI validation fix to catch common flag mistakes.
This can be imported and used before argparse to fix obvious errors.
"""

import sys
from typing import List, Tuple


def preprocess_cli_args(args: List[str]) -> Tuple[List[str], List[str]]:
    """
    Preprocess CLI arguments to fix common mistakes and provide warnings.

    Args:
        args: Raw command line arguments

    Returns:
        Tuple of (corrected_args, warnings)
    """
    corrected = []
    warnings = []

    # Common flag corrections
    corrections = {
        '-html': '--html',
        '-verbose': '--verbose',
        '-count': '--count',
        '-media': '--media',
        '-output': '--output',
        '-update': '--update',
        '-quiet': '--quiet'
    }

    for arg in args:
        if arg in corrections:
            corrected_arg = corrections[arg]
            corrected.append(corrected_arg)
            warnings.append(f"Corrected '{arg}' to '{corrected_arg}'")
        else:
            corrected.append(arg)

    return corrected, warnings


def validate_and_fix_command() -> List[str]:
    """
    Validate and fix command line arguments before main processing.

    Returns:
        Corrected command line arguments
    """
    original_args = sys.argv[1:]  # Skip script name

    if not original_args:
        return original_args

    corrected_args, warnings = preprocess_cli_args(original_args)

    # Show warnings if corrections were made
    if warnings:
        print("🔧 Auto-corrected command line flags:", file=sys.stderr)
        for warning in warnings:
            print(f"   • {warning}", file=sys.stderr)

        original_cmd = " ".join(["capcat"] + original_args)
        corrected_cmd = " ".join(["capcat"] + corrected_args)

        print(f"\nOriginal:  {original_cmd}", file=sys.stderr)
        print(f"Corrected: {corrected_cmd}", file=sys.stderr)
        print("", file=sys.stderr)  # Empty line

    return corrected_args


def detect_help_from_typo(args: List[str]) -> bool:
    """
    Detect if help was likely triggered by a typo rather than intentional.

    Args:
        args: Command line arguments

    Returns:
        True if help was likely triggered by typo
    """
    # Check for suspicious patterns that might have triggered help
    suspicious_patterns = ['-html', '-verbose', '-count', '-media', '-output', '-update']

    return any(pattern in args for pattern in suspicious_patterns)


if __name__ == "__main__":
    # Test the function
    test_cases = [
        ["fetch", "hn", "--verbose", "-html"],
        ["bundle", "tech", "-count", "10", "-media"],
        ["single", "URL", "--html", "--verbose"],  # Already correct
        ["fetch", "hn", "-help"],  # Intentional help
    ]

    for test_args in test_cases:
        print(f"Original: {test_args}")
        corrected, warnings = preprocess_cli_args(test_args)
        print(f"Corrected: {corrected}")
        if warnings:
            print(f"Warnings: {warnings}")
        print("---")