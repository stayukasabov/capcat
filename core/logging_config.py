#!/usr/bin/env python3
"""
Logging configuration for Capcat.
Provides centralized logging setup with configurable levels and optional file output.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# Global flag to suppress console logging during progress animations
_progress_active = False


def set_progress_active(active: bool):
    """Set whether progress animation is active (to suppress console logging)."""
    global _progress_active
    _progress_active = active


def is_progress_active() -> bool:
    """Check if progress animation is currently active."""
    return _progress_active


class ProgressFilter(logging.Filter):
    """Filter to suppress INFO/DEBUG logs during progress animation."""

    def filter(self, record):
        # During progress animation, only allow WARNING and above
        if _progress_active and record.levelno < logging.WARNING:
            return False
        return True


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[38;5;230m",  # Pale Yellow
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    # Emoji indicators for different log levels
    EMOJIS = {
        "DEBUG": "\033[36m\u269a\033[0m",
        "INFO": "\033[32m Catching→\033[0m",
        "WARNING": "\033[33m\u2622\033[0m",
        "ERROR": "\033[31m\u2612\033[0m",
        "CRITICAL": "\033[35m Catching→\033[0m",
    }

    def format(self, record):
        # Create a copy of the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)

        # Convert WARNING/ERROR to "Capcat Info: WARNING ..." format when progress is active
        if _progress_active and record.levelno >= logging.WARNING:
            # Format as "Capcat Info" with the warning message
            record_copy.levelname = f"{self.COLORS['INFO']}Capcat Info{self.COLORS['RESET']}"
            record_copy.msg = f"{self.COLORS['WARNING']}WARNING{self.COLORS['RESET']}: {record_copy.msg}"
        # Customize the levelname for INFO to show "Capcat Info"
        elif record_copy.levelname == "INFO":
            record_copy.levelname = (
                f"{self.COLORS['INFO']}Capcat Info{self.COLORS['RESET']}"
            )
        # Add color to the levelname copy for other levels
        elif record_copy.levelname in self.COLORS:
            record_copy.levelname = f"{self.COLORS[record_copy.levelname]}{record_copy.levelname}{self.COLORS['RESET']}"

        # Format the message
        formatted_msg = super().format(record_copy)

        # If progress is active and this is a warning/error, clear line first and add newline after
        if _progress_active and record.levelno >= logging.WARNING:
            formatted_msg = "\r\033[K" + formatted_msg + "\n"
        # Only clear line if progress is NOT active
        # (progress animation handles its own line clearing)
        elif sys.stdout.isatty() and not _progress_active:
            formatted_msg = "\r\033[K" + formatted_msg

        return formatted_msg


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    quiet: bool = False,
    verbose: bool = False,
) -> logging.Logger:
    """
    Setup logging configuration for Capcat.

    Args:
        level: Base logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file: Optional file path to write logs to
        quiet: If True, only show warnings and errors
        verbose: If True, show debug messages

    Returns:
        Configured logger instance
    """
    # Determine actual log level
    if quiet:
        console_level = logging.WARNING
    elif verbose:
        console_level = logging.DEBUG
    else:
        console_level = getattr(logging, level.upper(), logging.INFO)

    # Create main logger
    logger = logging.getLogger("capcat")
    logger.setLevel(logging.DEBUG)  # Capture all levels, handlers will filter

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)

    # Add progress filter to suppress logs during animation
    console_handler.addFilter(ProgressFilter())

    # Use colored formatter for console
    if quiet:
        console_formatter = ColoredFormatter(fmt="%(message)s")
    else:
        console_formatter = ColoredFormatter(
            fmt="%(levelname)s: %(message)s", datefmt="%H:%M:%S"
        )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # File gets all messages

        # File formatter without colors but with timestamps
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "") -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__ from the calling module)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"capcat.{name}")
    return logging.getLogger("capcat")


def set_verbosity(verbose: bool = False, quiet: bool = False):
    """
    Dynamically change the verbosity of the console handler.

    Args:
        verbose: Show debug messages
        quiet: Show only warnings and errors
    """
    logger = logging.getLogger("capcat")

    # Find the console handler
    for handler in logger.handlers:
        if (
            isinstance(handler, logging.StreamHandler)
            and handler.stream == sys.stdout
        ):
            if quiet:
                handler.setLevel(logging.WARNING)
            elif verbose:
                handler.setLevel(logging.DEBUG)
            else:
                handler.setLevel(logging.INFO)
            break
