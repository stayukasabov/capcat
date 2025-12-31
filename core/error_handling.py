#!/usr/bin/env python3
"""
Comprehensive error handling and recovery system for Capcat.

This module provides:
- Custom exception classes for different error types
- Dependency validation and auto-recovery
- Retry mechanisms with exponential backoff
- Error correlation and monitoring
- Graceful degradation strategies
"""

import sys
import time
import subprocess
import traceback
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union, Callable
from dataclasses import dataclass, field
from functools import wraps
import logging

# Import core modules with error handling
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class ErrorSeverity(Enum):
    """Error severity levels for categorization and handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification and handling strategies."""
    DEPENDENCY = "dependency"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    CONFIGURATION = "configuration"
    SOURCE_PROCESSING = "source_processing"
    MEDIA_DOWNLOAD = "media_download"
    VALIDATION = "validation"
    RUNTIME = "runtime"


@dataclass
class ErrorContext:
    """Context information for error analysis and correlation."""
    timestamp: float = field(default_factory=time.time)
    operation: str = ""
    source_id: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    retry_count: int = 0
    correlation_id: Optional[str] = None
    user_data: Dict[str, Any] = field(default_factory=dict)


class CapcatError(Exception):
    """Base exception for all Capcat-specific errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.RUNTIME,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        recoverable: bool = True,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.recoverable = recoverable
        self.original_error = original_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/monitoring."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "timestamp": self.context.timestamp,
            "operation": self.context.operation,
            "source_id": self.context.source_id,
            "url": self.context.url,
            "file_path": self.context.file_path,
            "retry_count": self.context.retry_count,
            "correlation_id": self.context.correlation_id,
            "original_error": str(self.original_error) if self.original_error else None,
            "traceback": traceback.format_exc()
        }


class DependencyError(CapcatError):
    """Raised when required dependencies are missing or corrupted."""

    def __init__(self, message: str, dependency_name: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DEPENDENCY,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.dependency_name = dependency_name


class NetworkError(CapcatError):
    """Raised for network-related issues."""

    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.status_code = status_code


class SourceProcessingError(CapcatError):
    """Raised during source-specific processing errors."""

    def __init__(self, message: str, source_id: str, **kwargs):
        context = kwargs.get('context', ErrorContext())
        context.source_id = source_id
        kwargs['context'] = context

        super().__init__(
            message,
            category=ErrorCategory.SOURCE_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ConfigurationError(CapcatError):
    """Raised for configuration-related errors."""

    def __init__(self, message: str, config_file: Optional[str] = None, **kwargs):
        context = kwargs.get('context', ErrorContext())
        if config_file:
            context.file_path = config_file
        kwargs['context'] = context

        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class MediaDownloadError(CapcatError):
    """Raised during media download failures."""

    def __init__(self, message: str, media_url: str, **kwargs):
        context = kwargs.get('context', ErrorContext())
        context.url = media_url
        kwargs['context'] = context

        super().__init__(
            message,
            category=ErrorCategory.MEDIA_DOWNLOAD,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class DependencyValidator:
    """Validates and manages application dependencies."""

    REQUIRED_PACKAGES = {
        'requests': '2.25.0',
        'beautifulsoup4': '4.9.0',
        'PyYAML': '5.4.0',
        'markdownify': '0.11.0',
        'markdown': '3.5.0',
        'pygments': '2.16.0',
        'charset_normalizer': '3.0.0'
    }

    def __init__(self, venv_path: Optional[Path] = None):
        self.venv_path = venv_path or Path("venv")
        self.logger = logging.getLogger(__name__)

    def validate_environment(self) -> Dict[str, bool]:
        """Validate the virtual environment and dependencies."""
        results = {
            'venv_exists': self._check_venv_exists(),
            'venv_activated': self._check_venv_activated(),
            'dependencies_installed': self._check_dependencies()
        }

        return results

    def _check_venv_exists(self) -> bool:
        """Check if virtual environment exists."""
        return (
            self.venv_path.exists() and
            (self.venv_path / "bin" / "python").exists()
        )

    def _check_venv_activated(self) -> bool:
        """Check if virtual environment is activated."""
        return (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        missing = []

        # Map package names to their import names
        import_names = {
            'requests': 'requests',
            'beautifulsoup4': 'bs4',
            'PyYAML': 'yaml',
            'markdownify': 'markdownify',
            'markdown': 'markdown',
            'pygments': 'pygments',
            'charset_normalizer': 'charset_normalizer'
        }

        for package, import_name in import_names.items():
            try:
                __import__(import_name)
            except ImportError:
                missing.append(package)

        if missing:
            self.logger.warning(f"Missing dependencies: {missing}")
            return False

        return True

    def auto_repair(self) -> bool:
        """Attempt to automatically repair dependency issues."""
        validation = self.validate_environment()

        try:
            # Recreate virtual environment if corrupted
            if not validation['venv_exists'] or not validation['venv_activated']:
                self.logger.info("Recreating virtual environment...")
                self._recreate_venv()

            # Reinstall dependencies if missing
            if not validation['dependencies_installed']:
                self.logger.info("Reinstalling dependencies...")
                self._reinstall_dependencies()

            return True

        except Exception as e:
            self.logger.error(f"Auto-repair failed: {e}")
            return False

    def _recreate_venv(self):
        """Recreate the virtual environment."""
        if self.venv_path.exists():
            import shutil
            shutil.rmtree(self.venv_path)

        subprocess.run([
            sys.executable, "-m", "venv", str(self.venv_path)
        ], check=True)

    def _reinstall_dependencies(self):
        """Reinstall all dependencies."""
        pip_path = self.venv_path / "bin" / "pip"
        requirements_file = Path("requirements.txt")

        if requirements_file.exists():
            subprocess.run([
                str(pip_path), "install", "-r", str(requirements_file)
            ], check=True)
        else:
            # Install individual packages
            for package in self.REQUIRED_PACKAGES:
                subprocess.run([
                    str(pip_path), "install", package
                ], check=True)


class RetryStrategy:
    """Implements retry logic with exponential backoff and circuit breaker."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt."""
        if attempt <= 0:
            return 0

        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)

        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # 50-100% of calculated delay

        return delay


def with_retry(
    max_retries: int = 3,
    retry_on: Union[Type[Exception], tuple] = Exception,
    strategy: Optional[RetryStrategy] = None
):
    """Decorator that adds retry logic to functions."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_strategy = strategy or RetryStrategy(max_retries=max_retries)
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    if attempt == max_retries:
                        raise e

                    delay = retry_strategy.get_delay(attempt + 1)
                    if delay > 0:
                        time.sleep(delay)

                    logging.getLogger(__name__).warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                    )

            raise last_exception

        return wrapper
    return decorator


class ErrorMonitor:
    """Monitors and correlates errors for analysis and alerting."""

    def __init__(self):
        self.error_history: List[Dict[str, Any]] = []
        self.error_counts: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)

    def record_error(self, error: CapcatError):
        """Record an error for monitoring and analysis."""
        error_data = error.to_dict()
        self.error_history.append(error_data)

        # Update error counts
        error_type = error_data['error_type']
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {error.message}", extra=error_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {error.message}", extra=error_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {error.message}", extra=error_data)
        else:
            self.logger.info(f"Low severity error: {error.message}", extra=error_data)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of recorded errors."""
        return {
            'total_errors': len(self.error_history),
            'error_counts_by_type': self.error_counts.copy(),
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }


class ErrorHandler:
    """Main error handling orchestrator."""

    def __init__(self):
        self.dependency_validator = DependencyValidator()
        self.error_monitor = ErrorMonitor()
        self.logger = logging.getLogger(__name__)

    def handle_startup_error(self, error: Exception) -> bool:
        """Handle errors during application startup."""
        if isinstance(error, ImportError):
            # Try to auto-repair dependency issues
            self.logger.info("Detected import error, attempting auto-repair...")
            return self.dependency_validator.auto_repair()

        return False

    def handle_runtime_error(self, error: Exception, context: Optional[ErrorContext] = None) -> bool:
        """Handle runtime errors with appropriate recovery strategies."""

        # Convert to CapcatError if needed
        if not isinstance(error, CapcatError):
            capcat_error = CapcatError(
                message=str(error),
                context=context,
                original_error=error
            )
        else:
            capcat_error = error

        # Record for monitoring
        self.error_monitor.record_error(capcat_error)

        # Attempt recovery based on error type
        if capcat_error.category == ErrorCategory.DEPENDENCY:
            return self.dependency_validator.auto_repair()
        elif capcat_error.category == ErrorCategory.NETWORK:
            # Network errors are often transient, log and continue
            return True
        elif capcat_error.category == ErrorCategory.MEDIA_DOWNLOAD:
            # Media download failures are not critical
            return True

        return capcat_error.recoverable


# Global error handler instance
_error_handler = ErrorHandler()


def handle_error(error: Exception, context: Optional[ErrorContext] = None) -> bool:
    """Global error handling function."""
    return _error_handler.handle_runtime_error(error, context)


def get_error_monitor() -> ErrorMonitor:
    """Get the global error monitor instance."""
    return _error_handler.error_monitor


def validate_dependencies() -> bool:
    """Validate application dependencies."""
    validation = _error_handler.dependency_validator.validate_environment()
    return all(validation.values())


def startup_check() -> bool:
    """Perform startup validation and auto-repair if needed."""
    try:
        if not validate_dependencies():
            return _error_handler.dependency_validator.auto_repair()
        return True
    except Exception as e:
        return _error_handler.handle_startup_error(e)