#!/usr/bin/env python3
"""
Automated Dependency Setup and Repair Script for Capcat

This script provides robust virtual environment management with:
- Intelligent venv validation and repair
- Dependency verification and installation
- Path corruption detection and fixing
- Fallback mechanisms for common issues
- Comprehensive logging and diagnostics

Usage:
    python3 scripts/setup_dependencies.py [options]

Options:
    --force-rebuild    Force complete venv rebuild
    --check-only       Only validate, don't install/repair
    --verbose         Enable detailed logging
    --requirements     Custom requirements file path
"""

import argparse
import json
import shutil
import subprocess
import sys

from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[0;31m"
    GREEN = "\033[38;5;157m"
    YELLOW = "\033[38;5;166m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


class DependencyManager:
    """
    Comprehensive dependency management system for Capcat.

    Handles virtual environment creation, validation, repair,
    and dependency installation with robust error handling.
    """

    def __init__(self, base_path: Optional[Path] = None, verbose: bool = False):
        """
        Initialize dependency manager.

        Args:
            base_path: Application base directory (auto-detected if None)
            verbose: Enable detailed logging
        """
        self.base_path = base_path or Path(__file__).parent.parent
        self.venv_dir = self.base_path / "venv"
        self.requirements_file = self.base_path / "requirements.txt"
        self.verbose = verbose

        # Dependency validation cache
        self.dependency_cache_file = self.venv_dir / ".dependency_cache.json"

    def log(self, message: str, color: str = Colors.GREEN, prefix: str = "INFO") -> None:
        """Print colored log message."""
        print(f"{color}{prefix}:{Colors.NC} {message}")

    def log_verbose(self, message: str) -> None:
        """Print verbose log message if verbose mode enabled."""
        if self.verbose:
            self.log(message, Colors.CYAN, "DEBUG")

    def log_error(self, message: str) -> None:
        """Print error message."""
        self.log(message, Colors.RED, "ERROR")

    def log_warning(self, message: str) -> None:
        """Print warning message."""
        self.log(message, Colors.YELLOW, "WARN")

    def log_success(self, message: str) -> None:
        """Print success message."""
        self.log(message, Colors.GREEN, "SUCCESS")

    def check_python_version(self) -> bool:
        """
        Verify Python version meets requirements.

        Returns:
            True if Python version is acceptable
        """
        try:
            version_info = sys.version_info
            if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
                self.log_error(f"Python 3.8+ required, found {version_info.major}.{version_info.minor}")
                return False

            self.log_verbose(f"Python version: {version_info.major}.{version_info.minor}.{version_info.micro}")
            return True

        except Exception as e:
            self.log_error(f"Failed to check Python version: {e}")
            return False

    def detect_venv_corruption(self) -> Tuple[bool, List[str]]:
        """
        Detect various types of virtual environment corruption.

        Returns:
            Tuple of (is_corrupted, list_of_issues)
        """
        issues = []

        if not self.venv_dir.exists():
            return False, []  # Not corrupted, just missing

        # Check for essential venv structure
        essential_paths = [
            self.venv_dir / "bin" / "python",
            self.venv_dir / "bin" / "pip",
            self.venv_dir / "lib",
            self.venv_dir / "pyvenv.cfg"
        ]

        for path in essential_paths:
            if not path.exists():
                issues.append(f"Missing essential file/directory: {path}")

        # Check for hardcoded path issues in pyvenv.cfg
        pyvenv_cfg = self.venv_dir / "pyvenv.cfg"
        if pyvenv_cfg.exists():
            try:
                content = pyvenv_cfg.read_text()
                # Look for paths that don't match current location
                current_python = shutil.which("python3")
                if current_python and current_python not in content:
                    # Check if the home path in pyvenv.cfg exists
                    for line in content.split('\n'):
                        if line.startswith('home = '):
                            home_path = line.split(' = ')[1].strip()
                            if not Path(home_path).exists():
                                issues.append(f"Python home path no longer exists: {home_path}")
                                break
            except Exception as e:
                issues.append(f"Cannot read pyvenv.cfg: {e}")

        # Test if python executable actually works
        python_exe = self.venv_dir / "bin" / "python"
        if python_exe.exists():
            try:
                result = subprocess.run(
                    [str(python_exe), "--version"],
                    capture_output=True,
                    timeout=10,
                    check=True
                )
                self.log_verbose(f"Venv Python works: {result.stdout.decode().strip()}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
                issues.append(f"Python executable doesn't work: {e}")

        return len(issues) > 0, issues

    def rebuild_venv(self) -> bool:
        """
        Completely rebuild the virtual environment.

        Returns:
            True if rebuild successful
        """
        self.log("Rebuilding virtual environment...")

        # Remove existing venv
        if self.venv_dir.exists():
            self.log_verbose(f"Removing existing venv at {self.venv_dir}")
            try:
                shutil.rmtree(self.venv_dir)
            except OSError as e:
                self.log_error(f"Failed to remove existing venv: {e}")
                return False

        # Create new venv
        try:
            self.log_verbose("Creating new virtual environment...")
            subprocess.run(
                ["python3", "-m", "venv", str(self.venv_dir)],
                check=True,
                cwd=str(self.base_path)
            )

            self.log_success("Virtual environment created successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to create virtual environment: {e}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error creating venv: {e}")
            return False

    def get_required_packages(self) -> List[str]:
        """
        Parse requirements.txt and return list of required packages.

        Returns:
            List of package names (without version specifiers)
        """
        if not self.requirements_file.exists():
            self.log_warning("No requirements.txt found")
            return []

        try:
            content = self.requirements_file.read_text()
            packages = []

            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before any version specifiers)
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
                    packages.append(package_name.strip())

            self.log_verbose(f"Required packages: {packages}")
            return packages

        except Exception as e:
            self.log_error(f"Failed to parse requirements.txt: {e}")
            return []

    def validate_dependencies(self, python_exe: str) -> Tuple[bool, List[str]]:
        """
        Validate that all required dependencies are installed and importable.

        Args:
            python_exe: Path to Python executable to test

        Returns:
            Tuple of (all_valid, list_of_missing_packages)
        """
        required_packages = self.get_required_packages()
        if not required_packages:
            return True, []

        missing_packages = []

        for package in required_packages:
            try:
                # Test if package can be imported
                result = subprocess.run(
                    [python_exe, "-c", f"import {package}"],
                    capture_output=True,
                    timeout=10
                )

                if result.returncode != 0:
                    # Try alternative import names for common packages
                    alt_names = {
                        'beautifulsoup4': 'bs4',
                        'PyYAML': 'yaml',
                        'markdownify': 'markdownify'
                    }

                    alt_name = alt_names.get(package)
                    if alt_name:
                        alt_result = subprocess.run(
                            [python_exe, "-c", f"import {alt_name}"],
                            capture_output=True,
                            timeout=10
                        )
                        if alt_result.returncode == 0:
                            continue  # Package is available under alternative name

                    missing_packages.append(package)
                    self.log_verbose(f"Missing package: {package}")
                else:
                    self.log_verbose(f"Package OK: {package}")

            except (subprocess.TimeoutExpired, Exception) as e:
                self.log_verbose(f"Error checking package {package}: {e}")
                missing_packages.append(package)

        return len(missing_packages) == 0, missing_packages

    def upgrade_pip(self, python_exe: str) -> bool:
        """
        Upgrade pip to latest version silently.

        Args:
            python_exe: Path to Python executable

        Returns:
            True if upgrade successful or already latest
        """
        try:
            self.log_verbose("Checking pip version...")

            # Upgrade pip silently
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,  # Suppress output
                timeout=60,
                check=True
            )

            # Only log if there was an actual upgrade
            if "Successfully installed pip" in result.stdout.decode():
                self.log_verbose("pip upgraded to latest version")
            else:
                self.log_verbose("pip already up to date")

            return True

        except subprocess.CalledProcessError as e:
            # pip upgrade failed, but continue anyway
            self.log_verbose(f"Could not upgrade pip: {e}")
            return True  # Non-critical, don't fail setup
        except subprocess.TimeoutExpired:
            self.log_verbose("pip upgrade timed out, continuing...")
            return True
        except Exception as e:
            self.log_verbose(f"Unexpected error upgrading pip: {e}")
            return True  # Non-critical, don't fail setup

    def install_dependencies(self, python_exe: str, force: bool = False) -> bool:
        """
        Install dependencies using pip.

        Args:
            python_exe: Path to Python executable
            force: Force reinstallation even if packages exist

        Returns:
            True if installation successful
        """
        if not self.requirements_file.exists():
            self.log_warning("No requirements.txt found, skipping dependency installation")
            return True

        # Upgrade pip to latest version first (silently)
        self.upgrade_pip(python_exe)

        self.log("Installing dependencies...")

        # Build pip command
        pip_cmd = [python_exe, "-m", "pip", "install"]

        if force:
            pip_cmd.append("--force-reinstall")

        pip_cmd.extend(["-r", str(self.requirements_file)])

        try:
            # Install with progress output
            result = subprocess.run(
                pip_cmd,
                cwd=str(self.base_path),
                check=True
            )

            self.log_success("Dependencies installed successfully")

            # Update dependency cache
            self._update_dependency_cache(python_exe)

            return True

        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to install dependencies: {e}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error installing dependencies: {e}")
            return False

    def _update_dependency_cache(self, python_exe: str) -> None:
        """Update dependency validation cache."""
        try:
            # Get list of installed packages
            result = subprocess.run(
                [python_exe, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                check=True
            )

            packages = json.loads(result.stdout.decode())
            cache_data = {
                'timestamp': subprocess.run(['date', '+%s'], capture_output=True).stdout.decode().strip(),
                'packages': {pkg['name']: pkg['version'] for pkg in packages},
                'python_exe': python_exe
            }

            # Ensure venv directory exists before writing cache
            self.venv_dir.mkdir(exist_ok=True)

            with open(self.dependency_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self.log_verbose("Updated dependency cache")

        except Exception as e:
            self.log_verbose(f"Failed to update dependency cache: {e}")

    def get_python_executable(self) -> str:
        """
        Get the best available Python executable.

        Returns:
            Path to Python executable (venv or system fallback)
        """
        venv_python = self.venv_dir / "bin" / "python"

        # Check if venv exists and is healthy
        if self.venv_dir.exists():
            is_corrupted, issues = self.detect_venv_corruption()

            if is_corrupted:
                self.log_warning("Virtual environment corruption detected:")
                for issue in issues:
                    self.log_warning(f"  - {issue}")

                # Attempt rebuild
                if not self.rebuild_venv():
                    self.log_error("Failed to rebuild venv, falling back to system Python")
                    return "python3"
            else:
                self.log_verbose("Virtual environment appears healthy")

        else:
            # Create new venv
            if not self.rebuild_venv():
                self.log_error("Failed to create venv, falling back to system Python")
                return "python3"

        # Return venv python if it exists
        if venv_python.exists():
            self.log(f"Using virtual environment: {self.venv_dir}")
            return str(venv_python)
        else:
            self.log_warning("Using system Python - dependencies may not be available")
            return "python3"

    def setup_dependencies(self, force_rebuild: bool = False, check_only: bool = False) -> bool:
        """
        Main method to setup and validate dependencies.

        Args:
            force_rebuild: Force complete venv rebuild
            check_only: Only validate, don't install/repair

        Returns:
            True if dependencies are ready
        """
        self.log("Starting dependency setup...")

        # Check Python version
        if not self.check_python_version():
            return False

        # Force rebuild if requested
        if force_rebuild:
            self.log("Force rebuild requested")
            if not check_only and not self.rebuild_venv():
                return False

        # Get Python executable
        python_exe = self.get_python_executable()

        # Validate dependencies
        deps_valid, missing = self.validate_dependencies(python_exe)

        if deps_valid:
            self.log_success("All dependencies are available")
            return True

        if missing:
            self.log_warning(f"Missing dependencies: {missing}")

        if check_only:
            return False

        # Install missing dependencies
        if not self.install_dependencies(python_exe):
            self.log_error("Failed to install dependencies")
            return False

        # Final validation
        deps_valid, still_missing = self.validate_dependencies(python_exe)

        if still_missing:
            self.log_error(f"Still missing after installation: {still_missing}")
            return False

        self.log_success("Dependencies setup completed successfully")
        return True


def main():
    """CLI entry point for dependency setup script."""
    parser = argparse.ArgumentParser(
        description="Automated dependency setup and repair for Capcat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/setup_dependencies.py                 # Normal setup
  python3 scripts/setup_dependencies.py --force-rebuild # Force venv rebuild
  python3 scripts/setup_dependencies.py --check-only    # Validate only
  python3 scripts/setup_dependencies.py --verbose       # Detailed logging
        """
    )

    parser.add_argument(
        '--force-rebuild',
        action='store_true',
        help='Force complete virtual environment rebuild'
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only validate dependencies, do not install or repair'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging'
    )

    parser.add_argument(
        '--requirements',
        type=Path,
        help='Custom requirements file path'
    )

    args = parser.parse_args()

    try:
        # Initialize dependency manager
        manager = DependencyManager(verbose=args.verbose)

        # Use custom requirements file if specified
        if args.requirements:
            manager.requirements_file = args.requirements

        # Setup dependencies
        success = manager.setup_dependencies(
            force_rebuild=args.force_rebuild,
            check_only=args.check_only
        )

        if success:
            manager.log_success("Dependency setup completed successfully")
            sys.exit(0)
        else:
            manager.log_error("Dependency setup failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()