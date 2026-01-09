#!/usr/bin/env python3
"""
Progress indicators and status reporting for Capcat.
Provides user-friendly feedback during long-running operations.
"""

import atexit
import re
import shutil
import signal
import sys
import threading
import time
from typing import Any, Callable, Optional

from .logging_config import get_logger


# Global cursor restoration mechanism
def _restore_cursor():
    """Global function to ensure cursor is always restored on exit."""
    if sys.stdout.isatty():
        sys.stdout.write("\033[?25h")  # Show cursor
        sys.stdout.flush()


# Register cursor restoration on program exit
atexit.register(_restore_cursor)


# Handle interruption signals
def _signal_handler(signum, frame):
    """Handle interruption signals and restore cursor."""
    _restore_cursor()
    sys.exit(1)


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def _get_terminal_width() -> int:
    """Get terminal width, with fallback to 80 columns."""
    try:
        return shutil.get_terminal_size().columns
    except (AttributeError, ValueError, OSError):
        return 80


def _strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text to measure visible width."""
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', text)


def _truncate_to_width(text: str, max_width: int) -> str:
    """
    Truncate text to fit within terminal width, preserving ANSI codes.

    Args:
        text: Text with ANSI codes
        max_width: Maximum visible character width

    Returns:
        Truncated text that fits within max_width
    """
    visible_text = _strip_ansi_codes(text)
    if len(visible_text) <= max_width:
        return text

    # Need to truncate - preserve ANSI codes while shortening visible text
    # Strategy: Remove characters from the middle section (operation name or stage info)
    # Keep spinner, progress bar, and percentage intact

    # Find components using ANSI pattern boundaries
    # Format: [spinner] [operation] [progress_bar] [count/percentage] [(stage)]

    # Simple truncation: just cut at max_width of visible chars
    visible_chars = 0
    result = []
    i = 0

    while i < len(text) and visible_chars < max_width:
        if text[i:i+2] == '\033[':
            # ANSI code - don't count toward visible width
            end = text.find('m', i)
            if end != -1:
                result.append(text[i:end+1])
                i = end + 1
            else:
                break
        else:
            result.append(text[i])
            visible_chars += 1
            i += 1

    return ''.join(result)


class ProgressIndicator:
    """
    Simple progress indicator for console output.
    Shows a spinner or percentage-based progress bar.
    """

    def __init__(
        self,
        message: str,
        total: Optional[int] = None,
        show_spinner: bool = True,
        spinner_style: str = "dots",
        show_count: bool = True,
    ):
        """
        Initialize progress indicator.

        Args:
            message: Message to display
            total: Total number of items (for percentage display)
            show_spinner: Whether to show animated spinner
            spinner_style: Style of spinner animation ('dots', 'wave', 'loading', 'pulse', 'bounce', 'modern')
            show_count: Whether to show current/total count (False shows only percentage)
        """
        self.message = message
        self.total = total
        self.show_spinner = show_spinner
        self.show_count = show_count
        self.current = 0
        self._stop_event = threading.Event()
        self._spinner_thread = None
        self.logger = get_logger(__name__)

        # Enhanced spinner characters with loading emulation
        self.spinner_sets = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "wave": [
                "▁",
                "▂",
                "▃",
                "▄",
                "▅",
                "▆",
                "▇",
                "█",
                "▇",
                "▆",
                "▅",
                "▄",
                "▃",
                "▂",
            ],
            "loading": [
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
            ],
            "pulse": ["◐", "◓", "◑", "◒"],
            "bounce": ["◐", "◓", "◑", "◒"],
            "modern": ["◜", "◝", "◞", "◟"],
        }
        self.spinner_chars = self.spinner_sets.get(
            spinner_style, self.spinner_sets["dots"]
        )
        self.spinner_index = 0

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def start(self):
        """Start the progress indicator."""
        # Suppress console logging during progress animation
        from .logging_config import set_progress_active
        set_progress_active(True)

        if self.show_spinner and sys.stdout.isatty():
            self._hide_cursor()  # Hide cursor for clean animation
            self._stop_event.clear()
            self._spinner_thread = threading.Thread(target=self._spin)
            self._spinner_thread.daemon = True
            self._spinner_thread.start()
        else:
            # Just print the initial message for non-TTY environments
            print(f"{self.message}...", flush=True)

    def stop(self, success_message: Optional[str] = None):
        """Stop the progress indicator."""
        if self._spinner_thread:
            self._stop_event.set()
            self._spinner_thread.join(timeout=0.1)
            self._clear_line()

        # Re-enable console logging
        from .logging_config import set_progress_active
        set_progress_active(False)

        # Always restore cursor when stopping
        self._show_cursor()

        # Always try to use colors if the terminal supports them
        use_colors = True

        # Spiral character for completion with color if supported
        if use_colors:
            dice_char = "\033[1;91m◐\033[0m"
        else:
            dice_char = "◐"

        if success_message:
            print(f"{dice_char}{success_message.upper()}")
        elif self.total and self.current > 0:
            print(
                f"{dice_char}{self.message.upper()} ({self.current}/{self.total} COMPLETED)"
            )
        else:
            print(f"{dice_char}{self.message.upper()} COMPLETED")

    def update(self, increment: int = 1, status_message: Optional[str] = None):
        """Update progress counter and optionally change status message."""
        self.current += increment
        if status_message:
            self.message = status_message

    def error(self, error_message: str):
        """Stop with error message."""
        if self._spinner_thread:
            self._stop_event.set()
            self._spinner_thread.join(timeout=0.1)
            self._clear_line()

        # Re-enable console logging
        from .logging_config import set_progress_active
        set_progress_active(False)

        # Always restore cursor on error
        self._show_cursor()

        # Always try to use colors if the terminal supports them
        use_colors = True

        # Dice character for error with color if supported
        if use_colors:
            dice_char = "\033[1;31m◒\033[0m"
        else:
            dice_char = "◒"
        print(f"{dice_char}{error_message.upper()}")

    def _create_progress_bar(self, percentage: float, width: int = 8) -> str:
        """Create a visual progress bar with loading animation."""
        filled = int(width * percentage / 100)
        remaining = width - filled

        # Orbit rings progression characters
        loading_chars = ["◉", "◎", "◎"]

        # Create the filled portion with solid circles (with spacing)
        filled_chars = ["\033[1;38;5;166m◉\033[0m"] * filled
        bar_filled = " ".join(filled_chars) if filled_chars else ""

        # Add a loading character at the edge for visual appeal
        edge_char = ""
        if filled < width and percentage > 0:
            edge_char = (
                "\033[1;38;5;166m" + loading_chars[1] + "\033[0m"
            )  # Use middle ring ◎
            remaining = max(0, remaining - 1)

        # Create the empty portion with bullseye rings (colorized with spacing)
        empty_chars = ["\033[1;38;5;166m◎\033[0m"] * remaining
        bar_empty = " ".join(empty_chars) if empty_chars else ""

        # Return progress bar with spacing between sections
        sections = [s for s in [bar_filled, edge_char, bar_empty] if s]
        return " ".join(sections)

    def _spin(self):
        """Internal spinner animation method with enhanced loading visualization."""
        while not self._stop_event.is_set():
            if sys.stdout.isatty():
                # Always try to use colors if the terminal supports them
                use_colors = True

                # Dice sequence animation with colors if supported
                if use_colors:
                    dice_chars = [
                        "\033[1;38;5;166m◐\033[0m",
                        "\033[1;38;5;166m◓\033[0m",
                        "\033[1;38;5;166m◑\033[0m",
                        "\033[1;38;5;166m◒\033[0m",
                    ]
                else:
                    dice_chars = ["◐", "◓", "◑", "◒"]
                dice_char = dice_chars[self.spinner_index % len(dice_chars)]

                # Spinner characters with colors if supported
                if use_colors:
                    spinner_chars = [
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                        "\033[38;5;166m CATCHING ▷\033[0m",
                    ]
                else:
                    spinner_chars = [
                        "CATCHING ▷",
                        "CATCHING ▷",
                        "CATCHING ▷",
                        "CATCHING ▷",
                        "CATCHING ▷",
                        "CATCHING ▷",
                        "CATCHING ▷",
                        "CATCHING ▷",
                    ]
                spinner_char = spinner_chars[
                    self.spinner_index % len(spinner_chars)
                ]

                if self.total and self.current > 0:
                    percentage = (self.current / self.total) * 100
                    progress_bar = self._create_progress_bar(percentage)
                    # Show count only if show_count is True
                    if self.show_count:
                        status = f"{dice_char}{spinner_char} \033[38;5;166m {self.message.upper()}\033[0m {progress_bar} \033[38;5;166m {self.current}/{self.total} ({percentage:.1f}%)\033[0m"
                    else:
                        status = f"{dice_char}{spinner_char} \033[38;5;166m {self.message.upper()}\033[0m {progress_bar} \033[38;5;166m ({percentage:.1f}%)\033[0m"
                else:
                    status = f"{dice_char}{spinner_char} \033[38;5;166m{self.message.upper()}...\033[0m"

                # Clear line and write status - ensure clean display
                if sys.stdout.isatty():
                    # Truncate status to terminal width to prevent line wrapping
                    term_width = _get_terminal_width()
                    status = _truncate_to_width(status, term_width - 1)
                    # Move to beginning of line, clear entire line, then write status
                    sys.stdout.write(f"\r\033[2K{status}")
                    sys.stdout.flush()

                self.spinner_index = (self.spinner_index + 1) % len(
                    spinner_chars
                )

            time.sleep(0.05)

    def _clear_line(self):
        """Clear the current line."""
        if sys.stdout.isatty():
            sys.stdout.write("\r\033[2K")
            sys.stdout.flush()

    def _hide_cursor(self):
        """Hide the cursor for clean progress display."""
        if sys.stdout.isatty():
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()

    def _show_cursor(self):
        """Show the cursor when progress is complete."""
        if sys.stdout.isatty():
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()


class BatchProgress:
    """
    Progress tracker for batch operations with detailed status reporting.
    """

    def __init__(
        self,
        operation_name: str,
        total_items: int,
        quiet: bool = False,
        verbose: bool = False,
        spinner_style: str = "activity",
    ):
        """
        Initialize batch progress tracker.

        Args:
            operation_name: Name of the batch operation
            total_items: Total number of items to process
            quiet: Whether to suppress detailed output
            verbose: Whether to show detailed item-by-item progress
            spinner_style: Style of spinner animation ('activity', 'progress', 'pulse', 'wave', 'dots', 'scan')
        """
        self.operation_name = operation_name
        self.total_items = total_items
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.quiet = quiet
        self._verbose = verbose  # Store verbose flag
        self.logger = get_logger(__name__)

        # Sub-progress tracking for individual item processing
        self.current_item_progress = 0.0  # 0.0 to 1.0
        self.current_item_stage = ""
        self.last_stage_update = time.time()
        self.last_known_stage = ""

        # Enhanced spinner with multiple animation sets
        self.spinner_sets = {
            "activity": [
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
                "CATCHING ▷ ",
            ],
            "progress": ["◐", "◓", "◑", "◒"],
            "pulse": ["◐", "◓", "◑", "◒"],
            "wave": [
                "▁",
                "▃",
                "▄",
                "▅",
                "▆",
                "▇",
                "█",
                "▇",
                "▆",
                "▅",
                "▄",
                "▃",
            ],
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "scan": ["▐", "▌", "▍", "▎", "▏", "▎", "▍", "▌"],
        }
        self.spinner_chars = self.spinner_sets.get(
            spinner_style, self.spinner_sets["activity"]
        )
        self.spinner_index = 0
        self.current_item = ""

        self.progress_indicator = ProgressIndicator(
            f"Processing {operation_name}",
            total=total_items,
            show_spinner=True,
        )

        # Continuous animation thread for smooth spinner rotation
        self._animation_thread = None
        self._animation_stop_event = threading.Event()
        self._last_update_time = time.time()
        self._animation_lock = threading.Lock()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            self.finish()
        except Exception as e:
            # Ensure animation thread is stopped even if finish() fails
            self._stop_animation_thread()
            self._show_cursor()
            # Re-enable console logging
            from .logging_config import set_progress_active
            set_progress_active(False)
            self.logger.error(f"Error during progress finish: {e}")
        finally:
            # Final safety net - ensure cursor is restored and logging re-enabled
            self._show_cursor()
            from .logging_config import set_progress_active
            set_progress_active(False)

    def _create_progress_bar(self, percentage: float, width: int = 6) -> str:
        """Create a visual progress bar with loading animation for batch operations."""
        filled = int(width * percentage / 100)
        remaining = width - filled

        # Orbit rings progression characters
        loading_chars = ["◉", "◎", "◎"]

        # Create the filled portion with solid circles (with spacing)
        filled_chars = ["\033[1;38;5;166m◉\033[0m"] * filled
        bar_filled = " ".join(filled_chars) if filled_chars else ""

        # Add a loading character at the edge for visual appeal
        edge_char = ""
        if filled < width and percentage > 0 and percentage < 100:
            edge_char = (
                "\033[1;38;5;166m" + loading_chars[1] + "\033[0m"
            )  # Use middle ring ◎
            remaining = max(0, remaining - 1)

        # Create the empty portion with bullseye rings (colorized with spacing)
        empty_chars = ["\033[1;38;5;166m◎\033[0m"] * remaining
        bar_empty = " ".join(empty_chars) if empty_chars else ""

        # Return progress bar with spacing between sections
        sections = [s for s in [bar_filled, edge_char, bar_empty] if s]
        return " ".join(sections)

    def _update_progress_display(self):
        """Update the progress display with current item sub-progress."""
        if self.quiet:
            return

        # Always try to use colors if the terminal supports them
        use_colors = True

        # Dice sequence animation with colors if supported
        if use_colors:
            dice_chars = [
                "\033[1;38;5;166m◐\033[0m",
                "\033[1;38;5;166m◓\033[0m",
                "\033[1;38;5;166m◑\033[0m",
                "\033[1;38;5;166m◒\033[0m",
            ]
        else:
            dice_chars = ["◐", "◓", "◑", "◒"]
        dice_char = dice_chars[self.spinner_index % len(dice_chars)]

        if use_colors:
            spinner_chars = [
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
            ]
        else:
            spinner_chars = [
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
            ]
        spinner_char = spinner_chars[self.spinner_index % len(spinner_chars)]

        if self.total_items > 0:
            # Calculate overall progress including sub-progress
            base_progress = self.completed / self.total_items
            item_progress = self.current_item_progress / self.total_items
            total_progress = (base_progress + item_progress) * 100

            # Create visual progress bar
            progress_bar = self._create_progress_bar(total_progress)

            # Create status with sub-progress info
            current_item = (
                self.completed + 1
                if self.completed < self.total_items
                else self.total_items
            )
            # Always show stage info when available, detect potential hangs
            current_time = time.time()
            time_since_update = current_time - self.last_stage_update

            if self.current_item_stage:
                # Update last known stage when we have current info
                self.last_known_stage = self.current_item_stage
                stage_info = f" ({self.current_item_stage.upper()})"
            elif self.last_known_stage and time_since_update > 120:
                # Show hang indicator only after 2 minutes
                # Show hang indicator only for non-complete stages after 2 minutes
                if self.last_known_stage != "complete":
                    stage_info = f" (STALLED: {self.last_known_stage.upper()})"
                else:
                    # For "complete" stage, don't show hanging - likely just finishing up
                    stage_info = f" ({self.last_known_stage.upper()})"
            elif self.last_known_stage:
                # Show last known stage normally
                stage_info = f" ({self.last_known_stage.upper()})"
            else:
                stage_info = ""

            # Truncate operation name if too long (max 20 chars + ellipsis)
            operation_display = self.operation_name.upper()
            if len(operation_display) > 20:
                operation_display = operation_display[:20] + "..."

            status = f"{dice_char}{spinner_char} \033[38;5;166m {operation_display}\033[0m {progress_bar} \033[38;5;166m {current_item}/{self.total_items} ({total_progress:.1f}%){stage_info}\033[0m"

            # Clear line and write status - ensure clean display
            if sys.stdout.isatty():
                # Truncate status to terminal width to prevent line wrapping
                term_width = _get_terminal_width()
                status = _truncate_to_width(status, term_width - 1)
                # Move to beginning of line, clear entire line, then write status
                sys.stdout.write(f"\r\033[2K{status}")
                sys.stdout.flush()

    def start(self):
        """Start the batch operation."""
        self.start_time = time.time()

        # Hide cursor for clean progress display
        self._hide_cursor()

        # Suppress console logging during progress animation
        from .logging_config import set_progress_active
        set_progress_active(True)

        if not self.quiet:
            # Always try to use colors if the terminal supports them
            use_colors = True

            # Show item count only for multiple items (hide for single items)
            if self.total_items > 1:
                if use_colors:
                    print(
                        f"\033[1;38;5;157m✦\033[0m STARTING {self.operation_name.upper()} ({self.total_items} ITEMS)"
                    )
                else:
                    print(
                        f"✦ STARTING {self.operation_name.upper()} ({self.total_items} ITEMS)"
                    )
            else:
                if use_colors:
                    print(
                        f"\033[1;38;5;157m✦\033[0m STARTING {self.operation_name.upper()}"
                    )
                else:
                    print(
                        f"✦ STARTING {self.operation_name.upper()}"
                    )

        self.logger.info(
            f"Starting {self.operation_name} batch operation ({self.total_items} items)"
        )

        # Start continuous animation thread
        self._start_animation_thread()

    def _hide_cursor(self):
        """Hide the cursor for clean progress display."""
        if sys.stdout.isatty():
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()

    def _show_cursor(self):
        """Show the cursor when progress is complete."""
        if sys.stdout.isatty():
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def update_item_progress(self, progress: float, stage: str = ""):
        """
        Update progress for the current item being processed.

        Args:
            progress: Progress from 0.0 to 1.0 for current item
            stage: Description of current processing stage
        """
        self.current_item_progress = max(0.0, min(1.0, progress))
        self.current_item_stage = stage

        # Update timestamp when stage info is provided
        if stage:
            self.last_stage_update = time.time()

        # Update display with rate limiting (max 10 FPS)
        if not self.quiet:
            current_time = time.time()
            if not hasattr(self, '_last_immediate_update') or (current_time - self._last_immediate_update) >= 0.1:
                self._last_immediate_update = current_time
                self._update_progress_display()

    def item_completed(
        self, success: bool = True, item_name: Optional[str] = None
    ):
        """
        Mark an item as completed.

        Args:
            success: Whether the item completed successfully
            item_name: Optional name of the completed item
        """
        if success:
            self.completed += 1
        else:
            self.failed += 1

        self.current_item = item_name or ""

        # Reset sub-progress for next item
        self.current_item_progress = 0.0
        self.current_item_stage = ""

        # Update last update time to refresh animation
        with self._animation_lock:
            self._last_update_time = time.time()
            # Force immediate display update
            self._force_display_update()

        # In verbose mode, show detailed item completion
        if (
            not self.quiet
            and hasattr(self, "_verbose")
            and self._verbose
            and item_name
        ):
            # Always try to use colors
            use_colors = True

            if use_colors:
                status_symbol = (
                    "\033[1;32m\u2611\033[0m"
                    if success
                    else "\033[1;31m\u2612\033[0m"
                )
                dice_char = "\033[1;38;5;166m◐\033[0m"
                spinner_char = "\033[38;5;166m CATCHING ▷\033[0m"
            else:
                status_symbol = "\u2611" if success else "\u2612"
                dice_char = "◐"
                spinner_char = " CATCHING ▷ "

            # Clear progress line before printing item completion
            if sys.stdout.isatty():
                sys.stdout.write("\r\033[2K")
                sys.stdout.flush()

            if self.total_items > 0:
                percentage = (self.completed / self.total_items) * 100
                progress_bar = self._create_progress_bar(percentage)
                print(
                    f"{dice_char}{spinner_char} {status_symbol} {item_name} {progress_bar} ({self.completed}/{self.total_items} - {percentage:.1f}%)"
                )
            else:
                print(
                    f"{dice_char}{spinner_char} {status_symbol} {item_name}"
                )

        # The continuous animation thread handles the normal progress display updates

        # Log individual item completion at debug level
        if item_name:
            status = "completed" if success else "failed"
            self.logger.debug(f"Item {status}: {item_name}")

    def get_summary(self) -> str:
        """Get a summary of the batch operation."""
        elapsed = time.time() - self.start_time
        success_rate = (self.completed / max(self.total_items, 1)) * 100

        return (
            f"{self.operation_name} summary: "
            f"{self.completed} successful, {self.failed} failed "
            f"({success_rate:.1f}% success rate) in {elapsed:.1f} seconds"
        )

    def finish(self):
        """Finish the batch operation and display summary."""
        # Stop animation thread FIRST to prevent racing conditions
        self._stop_animation_thread()

        # Re-enable console logging
        from .logging_config import set_progress_active
        set_progress_active(False)

        # Clear any progress line first for consistent spacing
        if sys.stdout.isatty():
            sys.stdout.write("\r\033[2K")
            sys.stdout.flush()

        summary = self.get_summary()

        # Always restore cursor when finishing
        self._show_cursor()

        if not self.quiet:
            # Always try to use colors if the terminal supports them
            use_colors = True

            # Prepare the main completion message
            if self.failed == 0:
                # Show count only for multiple items
                if self.total_items > 1:
                    if use_colors:
                        main_message = f"\033[1;38;5;157m◉\033[0m ALL {self.completed} {self.operation_name.upper()} COMPLETED SUCCESSFULLY!"
                    else:
                        main_message = f"◉ ALL {self.completed} {self.operation_name.upper()} COMPLETED SUCCESSFULLY!"
                else:
                    if use_colors:
                        main_message = f"\033[1;38;5;157m◉\033[0m {self.operation_name.upper()} COMPLETED SUCCESSFULLY!"
                    else:
                        main_message = f"◉ {self.operation_name.upper()} COMPLETED SUCCESSFULLY!"
            else:
                if use_colors:
                    main_message = f"\033[1;38;5;217m◯\033[0m {self.operation_name.upper()} FINISHED WITH {self.failed} FAILURES"
                else:
                    main_message = f"◯ {self.operation_name.upper()} FINISHED WITH {self.failed} FAILURES"

            print(main_message)

            # Print summary on next line
            if use_colors:
                print(f"\033[38;5;166m CATCHING ▷\033[0m {summary.upper()}")
            else:
                print(f" CATCHING ▷ {summary.upper()}")
        else:
            # In quiet mode, only show essential information
            if self.failed > 0:
                print(
                    f"\033[1;38;5;217m◯\033[0m  {self.operation_name.upper()} FINISHED WITH {self.failed} FAILURES"
                )

        self.logger.info(summary)

    def _start_animation_thread(self):
        """Start the continuous animation thread for smooth spinner rotation."""
        if self.quiet or not sys.stdout.isatty():
            return

        self._animation_stop_event.clear()
        self._animation_thread = threading.Thread(
            target=self._continuous_animation
        )
        self._animation_thread.daemon = True
        self._animation_thread.start()

    def _stop_animation_thread(self):
        """Stop the continuous animation thread."""
        if self._animation_thread:
            self._animation_stop_event.set()
            self._animation_thread.join(timeout=1.0)  # Increased timeout
            if self._animation_thread.is_alive():
                # Force termination if thread is still alive
                self.logger.warning("Animation thread did not stop gracefully")
            self._animation_thread = None

    def _continuous_animation(self):
        """Continuous animation loop that keeps the spinner rotating."""
        try:
            while not self._animation_stop_event.is_set():
                current_time = time.time()

                # Update animation every 100ms (10 FPS)
                try:
                    with self._animation_lock:
                        # Only update if it's been more than 100ms since last update
                        if current_time - self._last_update_time >= 0.1:
                            self.spinner_index = (
                                self.spinner_index + 1
                            ) % len(self.spinner_chars)
                            self._last_update_time = current_time

                            # Update display if not in verbose mode
                            if not (
                                hasattr(self, "_verbose") and self._verbose
                            ):
                                self._force_display_update()
                except Exception as e:
                    # Log but don't crash the animation thread
                    self.logger.debug(f"Animation display update error: {e}")

                # Sleep for 100ms, but break early if stop event is set
                if self._animation_stop_event.wait(0.1):
                    break
        except Exception as e:
            self.logger.error(f"Animation thread error: {e}")
        finally:
            # Ensure cursor is restored if animation thread exits unexpectedly
            self._show_cursor()

    def _force_display_update(self):
        """Force an immediate display update with current progress."""
        if self.quiet:
            return

        # Always try to use colors if the terminal supports them
        use_colors = True

        # Dice sequence animation with colors if supported
        if use_colors:
            dice_chars = [
                "\033[1;38;5;166m◐\033[0m",
                "\033[1;38;5;166m◓\033[0m",
                "\033[1;38;5;166m◑\033[0m",
                "\033[1;38;5;166m◒\033[0m",
            ]
        else:
            dice_chars = ["◐", "◓", "◑", "◒"]
        dice_char = dice_chars[self.spinner_index % len(dice_chars)]

        if use_colors:
            spinner_chars = [
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
                "\033[38;5;166m CATCHING ▷\033[0m",
            ]
        else:
            spinner_chars = [
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
                " CATCHING ▷ ",
            ]
        spinner_char = spinner_chars[self.spinner_index % len(spinner_chars)]

        if self.total_items > 0:
            # Calculate overall progress including sub-progress
            base_progress = self.completed / self.total_items
            item_progress = self.current_item_progress / self.total_items
            total_progress = (base_progress + item_progress) * 100

            # Create visual progress bar
            progress_bar = self._create_progress_bar(total_progress)

            # Create status with sub-progress info
            current_item = (
                self.completed + 1
                if self.completed < self.total_items
                else self.total_items
            )
            # Always show stage info when available, detect potential hangs
            current_time = time.time()
            time_since_update = current_time - self.last_stage_update

            if self.current_item_stage:
                # Update last known stage when we have current info
                self.last_known_stage = self.current_item_stage
                stage_info = f" ({self.current_item_stage.upper()})"
            elif self.last_known_stage and time_since_update > 120:
                # Show hang indicator only after 2 minutes
                # Show hang indicator only for non-complete stages after 2 minutes
                if self.last_known_stage != "complete":
                    stage_info = f" (STALLED: {self.last_known_stage.upper()})"
                else:
                    # For "complete" stage, don't show hanging - likely just finishing up
                    stage_info = f" ({self.last_known_stage.upper()})"
            elif self.last_known_stage:
                # Show last known stage normally
                stage_info = f" ({self.last_known_stage.upper()})"
            else:
                stage_info = ""

            # Truncate operation name if too long (max 20 chars + ellipsis)
            operation_display = self.operation_name.upper()
            if len(operation_display) > 20:
                operation_display = operation_display[:20] + "..."

            status = f"{dice_char}{spinner_char} \033[38;5;166m {operation_display}\033[0m {progress_bar} \033[38;5;166m {current_item}/{self.total_items} ({total_progress:.1f}%){stage_info}\033[0m"

            # Clear line and write status - ensure clean display
            if sys.stdout.isatty():
                # Truncate status to terminal width to prevent line wrapping
                term_width = _get_terminal_width()
                status = _truncate_to_width(status, term_width - 1)
                # Move to beginning of line, clear entire line, then write status
                sys.stdout.write(f"\r\033[2K{status}")
                sys.stdout.flush()


def with_progress(message: str, show_spinner: bool = True):
    """
    Decorator to add progress indication to functions.

    Args:
        message: Message to display during operation
        show_spinner: Whether to show animated spinner
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            with ProgressIndicator(message, show_spinner=show_spinner):
                return func(*args, **kwargs)

        return wrapper

    return decorator


class QuietProgress:
    """
    No-op progress indicator for quiet mode.
    Maintains the same interface but produces no output.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def start(self):
        pass

    def stop(self, success_message: Optional[str] = None):
        pass

    def update(self, increment: int = 1, status_message: Optional[str] = None):
        pass

    def update_item_progress(self, progress: float, stage: str = ""):
        """No-op implementation of update_item_progress for interface compatibility."""
        pass

    def error(self, error_message: str):
        pass

    def item_completed(
        self, success: bool = True, item_name: Optional[str] = None
    ):
        pass

    def get_summary(self) -> str:
        return ""

    def finish(self):
        pass


def get_progress_indicator(
    message: str, total: Optional[int] = None, quiet: bool = False
) -> ProgressIndicator:
    """
    Factory function to get appropriate progress indicator based on quiet mode and config.

    Args:
        message: Progress message
        total: Total number of items (optional)
        quiet: Whether to use quiet mode

    Returns:
        Progress indicator instance
    """
    if quiet:
        return QuietProgress(message, total)
    else:
        # Import here to avoid circular imports
        from .config import get_config

        config = get_config()
        return ProgressIndicator(
            message,
            total,
            show_spinner=config.ui.show_progress_animations,
            spinner_style=config.ui.progress_spinner_style,
        )


def get_batch_progress(
    operation_name: str,
    total_items: int,
    quiet: bool = False,
    verbose: bool = False,
) -> BatchProgress:
    """
    Factory function to get appropriate batch progress tracker based on quiet mode.

    Args:
        operation_name: Name of the batch operation
        total_items: Total number of items
        quiet: Whether to use quiet mode
        verbose: Whether to show detailed item-by-item progress

    Returns:
        Batch progress tracker instance
    """
    if quiet:
        return QuietProgress(operation_name, total_items)
    else:
        return BatchProgress(operation_name, total_items, quiet, verbose)
