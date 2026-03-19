#!/usr/bin/env python3
"""
Test cases for CLI validation and error handling.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from core.cli_validation import CLIValidator, CLIValidationError, validate_cli_args
from core.enhanced_argparse import EnhancedArgumentParser
from core.cli_recovery import CLIRecovery


class TestCLIValidation:
    """Test CLI validation functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.validator = CLIValidator()

    def test_detect_single_dash_long_flags(self):
        """Test detection of single dash with long flag names."""
        test_cases = [
            ("capcat fetch hn --verbose -html", ["-html"]),
            ("capcat fetch hn -verbose -count 10", ["-verbose", "-count"]),
            ("capcat bundle tech -media -output ~/dir", ["-media", "-output"]),
            ("capcat single URL --html -update", ["-update"]),
            ("capcat fetch hn --html --verbose", []),  # Correct flags
        ]

        for command, expected_issues in test_cases:
            issues = self.validator.detect_flag_typos(command)

            # Check that all expected issues are detected
            for expected in expected_issues:
                assert any(expected in issue for issue in issues), \
                    f"Expected to detect '{expected}' in command: {command}"

    def test_suggest_correct_command(self):
        """Test command correction suggestions."""
        test_cases = [
            (
                "capcat fetch hn --verbose -html",
                "capcat fetch hn --verbose --html"
            ),
            (
                "capcat fetch hn -verbose -count 10 -media",
                "capcat fetch hn --verbose --count 10 --media"
            ),
            (
                "capcat bundle tech --html --count 15",
                None  # Already correct
            ),
        ]

        for original, expected in test_cases:
            result = self.validator.suggest_correct_command(original)
            assert result == expected, f"Expected '{expected}', got '{result}' for: {original}"

    def test_common_flag_mistakes_mapping(self):
        """Test that common mistakes are properly mapped to suggestions."""
        assert "-html" in self.validator.common_flag_mistakes
        assert "-verbose" in self.validator.common_flag_mistakes
        assert "-count" in self.validator.common_flag_mistakes

        assert "--html or -H" in self.validator.common_flag_mistakes["-html"]
        assert "--verbose or -V" in self.validator.common_flag_mistakes["-verbose"]


class TestEnhancedArgumentParser:
    """Test enhanced argument parser functionality."""

    def test_normal_parsing_works(self):
        """Test that normal argument parsing still works correctly."""
        parser = EnhancedArgumentParser(prog='test')
        parser.add_argument('--html', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--count', type=int, default=30)
        parser.add_argument('sources', nargs='?')

        # Test correct command
        args = parser.parse_args(['hn', '--html', '--verbose', '--count', '10'])

        assert args.sources == 'hn'
        assert args.html is True
        assert args.verbose is True
        assert args.count == 10

    def test_help_flag_detection(self):
        """Test detection of help flags in malformed commands."""
        parser = EnhancedArgumentParser(prog='test')
        parser.add_argument('--html', action='store_true')
        parser.add_argument('sources', nargs='?')

        # This should detect that -h in -html triggered help
        with patch('sys.stderr') as mock_stderr:
            with pytest.raises(SystemExit):
                parser.parse_args(['hn', '-html'])  # Should trigger help due to -h


class TestCLIRecovery:
    """Test CLI error recovery functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.recovery = CLIRecovery()

    def test_suspicious_flag_detection(self):
        """Test detection of suspicious flags that might cause errors."""
        suspicious_flags = ['-html', '-verbose', '-count', '-media']
        normal_flags = ['--html', '--verbose', '-H', '-V']

        for flag in suspicious_flags:
            assert self.recovery._is_suspicious_flag(flag), \
                f"Should detect '{flag}' as suspicious"

        for flag in normal_flags:
            assert not self.recovery._is_suspicious_flag(flag), \
                f"Should not detect '{flag}' as suspicious"

    def test_flag_suggestion(self):
        """Test flag correction suggestions."""
        test_cases = [
            ('-html', '--html'),
            ('-verbose', '--verbose'),
            ('-count', '--count'),
            ('-unknown', None),
        ]

        for flag, expected in test_cases:
            result = self.recovery._get_flag_suggestion(flag)
            assert result == expected, f"Expected '{expected}' for '{flag}', got '{result}'"

    def test_command_auto_correction(self):
        """Test automatic command correction."""
        test_cases = [
            (
                "capcat fetch hn -html -verbose",
                "capcat fetch hn --html --verbose"
            ),
            (
                "capcat bundle tech -count 10 -media",
                "capcat bundle tech --count 10 --media"
            ),
        ]

        for original, expected in test_cases:
            result = self.recovery._auto_correct_command(original)
            assert result == expected, f"Expected '{expected}', got '{result}'"

    def test_alternative_command_suggestions(self):
        """Test alternative command suggestions."""
        suggestions = self.recovery.suggest_alternative_commands(
            "capcat fetch hn -html", "fetch"
        )

        assert len(suggestions) > 0
        assert any("fetch hn --html" in suggestion for suggestion in suggestions)
        assert any("list sources" in suggestion for suggestion in suggestions)

    @patch('sys.stderr')
    def test_help_triggered_by_error_handling(self, mock_stderr):
        """Test handling of help triggered by syntax errors."""
        args = ['hn', '-html', '--verbose']

        result = self.recovery.handle_help_triggered_by_error(args)

        assert result is True  # Should detect and handle the error
        # Should have printed guidance to stderr
        assert mock_stderr.write.called


class TestIntegration:
    """Integration tests for the full CLI validation system."""

    def test_end_to_end_error_detection(self):
        """Test complete error detection and recovery flow."""
        # Simulate the problematic command
        command_args = ['fetch', 'hn', '--verbose', '-html']

        validator = CLIValidator()
        issues = validator.detect_flag_typos(' '.join(['capcat'] + command_args))

        assert len(issues) > 0
        assert any('-html' in issue for issue in issues)

        suggestion = validator.suggest_correct_command(' '.join(['capcat'] + command_args))
        assert '--html' in suggestion
        assert ' -html' not in suggestion  # single-dash form must not appear as standalone flag

    @patch('sys.stderr')
    def test_user_guidance_flow(self, mock_stderr):
        """Test the complete user guidance flow."""
        from core.cli_recovery import handle_cli_error_recovery

        # Test with problematic args
        problematic_args = ['hn', '--verbose', '-html']

        result = handle_cli_error_recovery(problematic_args, 'fetch')

        assert result is True
        # Should have provided guidance
        assert mock_stderr.write.called


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_cli_validation.py -v
    pytest.main([__file__, "-v"])