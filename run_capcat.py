#!/usr/bin/env python3
"""
Capcat - News Article Archiving System (Enhanced Python Wrapper)

Refactored wrapper with robust dependency management, intelligent error
handling, and comprehensive validation. Integrates with the automated
dependency setup system.

Author: Stayu Kasabov (https://stayux.com)
License: MIT-Style Non-Commercial
Copyright (c) 2025 Stayu Kasabov
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class CapcatExecutionError(Exception):
    """Custom exception for Capcat execution failures."""
    pass


class DependencyError(Exception):
    """Custom exception for dependency-related failures."""
    pass


class CapcatWrapperRefactored:
    """Enhanced wrapper with robust dependency management and error handling.

    Provides intelligent dependency validation, automatic repair, comprehensive
    error handling, and fallback mechanisms for reliability.

    Attributes:
        script_dir: Application root directory path
        capcat_py: Path to main capcat.py script
        dependency_script: Path to automated dependency setup script
    """

    def __init__(self) -> None:
        """Initialize the wrapper with path validation.

        Sets up script directory paths and validates that essential files exist.
        Falls back to basic dependency management if enhanced script missing.

        Raises:
            CapcatExecutionError: If capcat.py not found in script directory
        """
        self.script_dir = Path(__file__).parent.absolute()
        self.capcat_py = self.script_dir / "capcat.py"
        self.dependency_script = (
            self.script_dir / "scripts" / "setup_dependencies.py"
        )

        # Validate essential files exist
        self._validate_installation()

    def _validate_installation(self) -> None:
        """Validate that essential files exist.

        Checks for capcat.py and dependency setup script. Sets dependency_script
        to None if enhanced script missing (triggers basic fallback).

        Raises:
            CapcatExecutionError: If capcat.py not found
        """
        if not self.capcat_py.exists():
            raise CapcatExecutionError(
                f"capcat.py not found in {self.script_dir}"
            )

        if not self.dependency_script.exists():
            # Fall back to basic dependency management if enhanced
            # script missing
            self.dependency_script = None

    def _log_message(
        self, message: str, level: str = "INFO",
        color: str = "\033[38;5;157m"
    ) -> None:
        """Log formatted message with color.

        Args:
            message: Text to log
            level: Log level string (INFO, ERROR, WARNING, SUCCESS)
            color: ANSI color code for formatting
        """
        reset = "\033[0m"
        print(f"{color}{level}:{reset} {message}")

    def _log_error(self, message: str) -> None:
        """Log error message.

        Args:
            message: Error message to display
        """
        self._log_message(message, "ERROR", "\033[0;31m")

    def _log_warning(self, message: str) -> None:
        """Log warning message.

        Args:
            message: Warning message to display
        """
        self._log_message(message, "WARNING", "\033[38;5;166m")

    def _log_success(self, message: str) -> None:
        """Log success message.

        Args:
            message: Success message to display
        """
        self._log_message(message, "SUCCESS", "\033[38;5;157m")

    def _run_dependency_setup(self, force_rebuild: bool = False) -> bool:
        """Run the automated dependency setup script.

        Falls back to basic setup if enhanced script unavailable.

        Args:
            force_rebuild: Force complete venv rebuild

        Returns:
            True if setup successful, False otherwise

        Raises:
            subprocess.CalledProcessError: If dependency setup command fails
        """
        if not self.dependency_script:
            self._log_warning(
                "Enhanced dependency setup not available, "
                "using basic fallback"
            )
            return self._basic_dependency_setup()

        try:
            cmd = [sys.executable, str(self.dependency_script)]
            if force_rebuild:
                cmd.append('--force-rebuild')

            self._log_message("Running automated dependency setup...")

            result = subprocess.run(
                cmd,
                cwd=str(self.script_dir),
                check=True
            )

            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            self._log_error(f"Dependency setup failed: {e}")
            return False
        except Exception as e:
            self._log_error(f"Unexpected error in dependency setup: {e}")
            return False

    def _basic_dependency_setup(self) -> bool:
        """Basic fallback dependency setup when enhanced script unavailable.

        Creates venv if missing and installs requirements.txt dependencies.

        Returns:
            True if basic setup successful, False otherwise

        Raises:
            subprocess.CalledProcessError: If venv creation or pip install fails
        """
        try:
            venv_dir = self.script_dir / "venv"
            requirements_file = self.script_dir / "requirements.txt"

            # Create venv if missing
            if not venv_dir.exists():
                self._log_message("Creating virtual environment...")
                subprocess.run(
                    ["python3", "-m", "venv", str(venv_dir)],
                    check=True,
                    cwd=str(self.script_dir)
                )

            # Install requirements if file exists
            if requirements_file.exists():
                python_exe = venv_dir / "bin" / "python"
                if python_exe.exists():
                    self._log_message("Installing dependencies...")
                    subprocess.run(
                        [
                            str(python_exe), "-m", "pip", "install",
                            "-r", str(requirements_file)
                        ],
                        check=True,
                        cwd=str(self.script_dir)
                    )

            return True

        except subprocess.CalledProcessError as e:
            self._log_error(f"Basic dependency setup failed: {e}")
            return False
        except Exception as e:
            self._log_error(f"Unexpected error in basic setup: {e}")
            return False

    def _get_python_executable(self) -> str:
        """Get the best available Python executable.

        Tries venv Python first, tests if it works, then falls back to
        system Python if necessary.

        Returns:
            Path to Python executable

        Raises:
            DependencyError: If no suitable Python found
        """
        venv_python = self.script_dir / "venv" / "bin" / "python"

        # Try venv python first
        if venv_python.exists():
            try:
                # Test if it works
                result = subprocess.run(
                    [str(venv_python), "--version"],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                self._log_message(f"Using virtual environment Python")
                return str(venv_python)
            except (subprocess.CalledProcessError,
                    subprocess.TimeoutExpired):
                self._log_warning(
                    "Virtual environment Python is broken, "
                    "trying system Python"
                )

        # Fall back to system python
        import shutil
        system_python = shutil.which("python3")
        if system_python:
            self._log_warning(
                "Using system Python - dependencies may not be "
                "available"
            )
            return system_python

        raise DependencyError("No suitable Python executable found")

    def _validate_dependencies(self, python_exe: str) -> bool:
        """Quick validation of critical dependencies.

        Tests imports of requests, yaml, and bs4 (BeautifulSoup).

        Args:
            python_exe: Python executable to test

        Returns:
            True if basic dependencies available, False otherwise
        """
        # bs4 is BeautifulSoup
        critical_packages = ['requests', 'yaml', 'bs4']

        for package in critical_packages:
            try:
                result = subprocess.run(
                    [python_exe, "-c", f"import {package}"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False
            except (subprocess.TimeoutExpired, Exception):
                return False

        return True

    def _handle_dependency_failure(self, python_exe: str) -> bool:
        """Handle dependency validation failure with repair attempts.

        Tries automated setup first, then force rebuild as last resort.

        Args:
            python_exe: Python executable that failed validation

        Returns:
            True if repair successful, False otherwise
        """
        self._log_warning(
            "Dependency validation failed, attempting repair..."
        )

        # Try automated setup first
        if self._run_dependency_setup():
            # Re-validate after setup
            new_python = self._get_python_executable()
            if self._validate_dependencies(new_python):
                return True

        # Try force rebuild as last resort
        self._log_warning(
            "Attempting force rebuild of virtual environment..."
        )
        if self._run_dependency_setup(force_rebuild=True):
            # Final validation
            final_python = self._get_python_executable()
            return self._validate_dependencies(final_python)

        return False

    def _should_show_success_message(self, args: List[str]) -> bool:
        """Determine if success message should be shown.

        Suppresses success message for help/version/list commands and
        detects when help was triggered by flag syntax errors.

        Args:
            args: Command line arguments

        Returns:
            True if success message appropriate, False otherwise
        """
        help_flags = ["--help", "-h", "--version", "-v", "list"]

        # Check for explicit help/version flags
        if any(arg in help_flags for arg in args):
            return False

        # Check for common flag mistakes that trigger help accidentally
        problematic_flags = ["-html", "-verbose", "-count", "-media", "-output", "-update", "-quiet"]
        detected_issues = [flag for flag in problematic_flags if flag in args]

        if detected_issues:
            # Help was likely triggered by syntax error, don't show success
            self._show_intelligent_help(args, detected_issues)
            return False

        return len(args) > 0

    def _show_intelligent_help(self, args: List[str], detected_issues: List[str]):
        """Show intelligent help when flag syntax errors are detected.

        Args:
            args: Original command line arguments
            detected_issues: List of problematic flags detected
        """
        print("\nCommand Error: Flag syntax issues detected", file=sys.stderr)

        # Show specific corrections
        corrections = {
            '-html': '--html',
            '-verbose': '--verbose',
            '-count': '--count',
            '-media': '--media',
            '-output': '--output',
            '-update': '--update',
            '-quiet': '--quiet'
        }

        print("\nDetected issues and corrections:", file=sys.stderr)
        for issue in detected_issues:
            if issue in corrections:
                print(f"  - '{issue}' should be '{corrections[issue]}'", file=sys.stderr)

        # Auto-correct and show suggestion
        corrected_args = []
        for arg in args:
            corrected_args.append(corrections.get(arg, arg))

        original_cmd = " ".join(["./capcat"] + args)
        corrected_cmd = " ".join(["./capcat"] + corrected_args)

        print(f"\nSuggested command:", file=sys.stderr)
        print(f"  {corrected_cmd}", file=sys.stderr)

        # Show context-specific help
        command_type = args[0] if args else None
        if command_type in ['fetch', 'bundle', 'single']:
            print(f"\nQuick help for '{command_type}' command:", file=sys.stderr)
            if command_type == 'fetch':
                print("  ./capcat fetch <sources> --html --count 10", file=sys.stderr)
                print("  ./capcat fetch hn --verbose --media", file=sys.stderr)
            elif command_type == 'bundle':
                print("  ./capcat bundle tech --html --count 15", file=sys.stderr)
                print("  ./capcat bundle news --verbose", file=sys.stderr)
            elif command_type == 'single':
                print("  ./capcat single <URL> --html --media", file=sys.stderr)

        print(f"\nUse './capcat {command_type} --help' for all options", file=sys.stderr)

    def execute_capcat(self, args: List[str]) -> int:
        """Execute capcat.py with comprehensive error handling.

        Validates dependencies, attempts repair if needed, and executes capcat
        with proper subprocess management and error handling.

        Args:
            args: Command line arguments to pass to capcat.py

        Returns:
            Exit code from capcat execution

        Raises:
            CapcatExecutionError: If execution fails
            DependencyError: If dependencies cannot be resolved
        """
        # Get Python executable
        try:
            python_exe = self._get_python_executable()
        except DependencyError as e:
            self._log_error(str(e))
            raise

        # Validate dependencies
        if not self._validate_dependencies(python_exe):
            # Attempt repair
            if not self._handle_dependency_failure(python_exe):
                raise DependencyError(
                    "Dependencies validation failed and automatic "
                    "repair was unsuccessful. "
                    "Try running: python3 scripts/setup_dependencies.py "
                    "--force-rebuild"
                )

            # Get updated python executable after repair
            python_exe = self._get_python_executable()

        # Execute capcat
        cmd = [python_exe, str(self.capcat_py)] + args

        try:
            result = subprocess.run(cmd, cwd=str(self.script_dir))

            # Log appropriate message based on result
            if (result.returncode == 0 and
                    self._should_show_success_message(args)):
                self._log_success("Capcat completed successfully!")
            elif result.returncode != 0:
                self._log_error(
                    f"Capcat exited with error code: "
                    f"{result.returncode}"
                )

            return result.returncode

        except FileNotFoundError:
            raise CapcatExecutionError(
                f"Python executable not found: {python_exe}"
            )
        except KeyboardInterrupt:
            self._log_warning("Operation interrupted by user")
            return 130
        except Exception as e:
            raise CapcatExecutionError(
                f"Unexpected error executing capcat: {e}"
            )

    def run(self) -> None:
        """Main execution method with comprehensive error handling.

        Handles all exceptions and exits with appropriate codes. Provides
        manual recovery instructions on failure.

        Exit Codes:
            0: Success
            1: Unexpected error
            2: Dependency error
            3: Execution error
            130: User interrupt (Ctrl+C)
        """
        try:
            exit_code = self.execute_capcat(sys.argv[1:])
            sys.exit(exit_code)

        except DependencyError as e:
            self._log_error(f"Dependency Error: {e}")
            self._log_message("Manual dependency setup:")
            self._log_message("  1. rm -rf venv")
            self._log_message("  2. python3 -m venv venv")
            self._log_message("  3. source venv/bin/activate")
            self._log_message("  4. pip install -r requirements.txt")
            sys.exit(2)

        except CapcatExecutionError as e:
            self._log_error(f"Execution Error: {e}")
            sys.exit(3)

        except KeyboardInterrupt:
            self._log_warning("Operation cancelled by user")
            sys.exit(130)

        except Exception as e:
            self._log_error(f"Unexpected error: {e}")
            self._log_message(
                "Please report this issue with the full error message"
            )
            sys.exit(1)


def main() -> None:
    """Entry point for the enhanced wrapper.

    Instantiates CapcatWrapperRefactored and runs the application with
    comprehensive dependency management and error handling.
    """
    wrapper = CapcatWrapperRefactored()
    wrapper.run()


if __name__ == "__main__":
    main()