#!/usr/bin/env python3
"""
Enhanced command logging for CLI debugging and audit trail.
"""

import time
import json
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from core.logging_config import get_logger


class CommandLogger:
    """Logger for CLI command execution and debugging."""

    def __init__(self):
        self.logger = get_logger("cli_commands")
        self.session_start = time.time()

    def log_command_start(self, command: str, args: Dict[str, Any], raw_args: List[str]):
        """
        Log command execution start with full context.

        Args:
            command: Command name (e.g., 'fetch', 'bundle')
            args: Parsed arguments dictionary
            raw_args: Raw command line arguments
        """
        context = {
            "event": "command_start",
            "command": command,
            "parsed_args": args,
            "raw_command": " ".join(["capcat"] + raw_args),
            "timestamp": time.time(),
            "session_time": time.time() - self.session_start
        }

        self.logger.info(
            f"Command started: {command}",
            extra={"cli_context": context}
        )

        # Also log to debug for troubleshooting
        self.logger.debug(f"Raw command line: {' '.join(['capcat'] + raw_args)}")
        self.logger.debug(f"Parsed arguments: {json.dumps(args, indent=2)}")

    def log_command_end(self, command: str, success: bool, duration: float,
                       error: Optional[str] = None):
        """
        Log command execution completion.

        Args:
            command: Command name
            success: Whether command succeeded
            duration: Execution duration in seconds
            error: Error message if failed
        """
        context = {
            "event": "command_end",
            "command": command,
            "success": success,
            "duration": duration,
            "timestamp": time.time(),
            "session_time": time.time() - self.session_start
        }

        if error:
            context["error"] = error

        level = "info" if success else "error"
        message = f"Command {'completed' if success else 'failed'}: {command} ({duration:.2f}s)"

        if error:
            message += f" - {error}"

        getattr(self.logger, level)(message, extra={"cli_context": context})

    def log_argument_error(self, command: str, error_type: str, error_message: str,
                          raw_args: List[str], suggestions: Optional[List[str]] = None):
        """
        Log argument parsing errors with suggestions.

        Args:
            command: Command name
            error_type: Type of error (e.g., 'flag_syntax', 'invalid_argument')
            error_message: Error description
            raw_args: Raw command line arguments
            suggestions: Suggested corrections
        """
        context = {
            "event": "argument_error",
            "command": command,
            "error_type": error_type,
            "error_message": error_message,
            "raw_command": " ".join(["capcat"] + raw_args),
            "suggestions": suggestions or [],
            "timestamp": time.time(),
            "session_time": time.time() - self.session_start
        }

        self.logger.warning(
            f"Argument error in {command}: {error_type} - {error_message}",
            extra={"cli_context": context}
        )

    def log_help_displayed(self, command: Optional[str], trigger_reason: str):
        """
        Log when help is displayed and why.

        Args:
            command: Command name (None for main help)
            trigger_reason: Why help was shown (e.g., 'help_flag', 'invalid_syntax')
        """
        context = {
            "event": "help_displayed",
            "command": command,
            "trigger_reason": trigger_reason,
            "timestamp": time.time(),
            "session_time": time.time() - self.session_start
        }

        self.logger.info(
            f"Help displayed for {command or 'main'}: {trigger_reason}",
            extra={"cli_context": context}
        )


# Global command logger instance
_command_logger = CommandLogger()


def get_command_logger() -> CommandLogger:
    """Get the global command logger instance."""
    return _command_logger


# Convenience functions
def log_command_start(command: str, args: Dict[str, Any], raw_args: List[str]):
    """Log command execution start."""
    get_command_logger().log_command_start(command, args, raw_args)


def log_command_end(command: str, success: bool, duration: float, error: Optional[str] = None):
    """Log command execution end."""
    get_command_logger().log_command_end(command, success, duration, error)


def log_argument_error(command: str, error_type: str, error_message: str,
                      raw_args: List[str], suggestions: Optional[List[str]] = None):
    """Log argument parsing error."""
    get_command_logger().log_argument_error(command, error_type, error_message, raw_args, suggestions)


def log_help_displayed(command: Optional[str], trigger_reason: str):
    """Log help display event."""
    get_command_logger().log_help_displayed(command, trigger_reason)