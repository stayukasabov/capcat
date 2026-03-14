#!/usr/bin/env python3
"""
Custom exceptions for Capcat application.
Provides structured error handling with user-friendly messages.
"""

from capcat.core.constants import ErrorCode


class CapcatError(Exception):
    """Base exception for all Capcat related errors."""

    def __init__(
        self,
        message: str,
        user_message: str = None,
        original_error: Exception = None,
        error_code: int = None,
    ):
        """Create a CapcatError with separate technical and user-facing messages.

        Args:
            message: Technical error message (logged, not shown to user).
            user_message: Human-readable message shown in the CLI. Defaults
                to *message* if not provided.
            original_error: The underlying exception that triggered this one,
                preserved for logging and ``to_dict()``.
            error_code: Numeric code from ``ErrorCode``. Defaults to
                ``ErrorCode.UNKNOWN_ERROR``.
        """
        super().__init__(message)
        self.user_message = user_message or message
        self.original_error = original_error
        self.error_code = error_code or ErrorCode.UNKNOWN_ERROR

    def __str__(self) -> str:
        """Return the user-facing message string."""
        return self.user_message

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/API responses.

        Returns:
            Dictionary with error details including code and messages

        Example:
            >>> try:
            ...     raise NetworkError("https://example.com")
            ... except NetworkError as e:
            ...     print(e.to_dict())
            {'error_code': 1001, 'message': 'Could not access...',
             'technical_message': 'Network error...', ...}
        """
        return {
            'error_code': self.error_code,
            'message': str(self),
            'technical_message': (
                str(self.args[0]) if self.args else None
            ),
            'original_error': (
                str(self.original_error)
                if self.original_error else None
            )
        }


class NetworkError(CapcatError):
    """Raised when network operations fail (DNS, timeout, HTTP errors)."""

    def __init__(self, url: str, original_error: Exception = None):
        """Create a NetworkError for a failed URL request.

        Args:
            url: The URL that could not be reached.
            original_error: The underlying ``requests`` exception.
        """
        message = f"Network error accessing {url}: {original_error}"
        user_message = (
            f"Could not access {url}. The server may be temporarily "
            "unavailable or the link may be broken."
        )
        super().__init__(
            message,
            user_message,
            original_error,
            ErrorCode.NETWORK_ERROR
        )
        self.url = url


class ContentFetchError(CapcatError):
    """Raised when an article's content cannot be extracted after a successful request."""

    def __init__(
        self,
        title: str,
        url: str,
        reason: str,
        original_error: Exception = None,
    ):
        """Create a ContentFetchError.

        Args:
            title: Article title (for the error message).
            url: Article URL that failed content extraction.
            reason: Human-readable explanation of why extraction failed.
            original_error: The underlying exception, if any.
        """
        message = f"Failed to fetch '{title}' from {url}: {reason}"
        user_message = f"Could not fetch article '{title}': {reason}"
        super().__init__(
            message,
            user_message,
            original_error,
            ErrorCode.CONTENT_FETCH_ERROR
        )
        self.title = title
        self.url = url


class ConfigurationError(CapcatError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_issue: str, suggestion: str = None):
        """Create a ConfigurationError.

        Args:
            config_issue: Description of what is wrong with the config.
            suggestion: Optional fix suggestion appended to the user message.
        """
        message = f"Configuration error: {config_issue}"
        user_message = f"Configuration problem: {config_issue}"
        if suggestion:
            user_message += f" {suggestion}"
        super().__init__(
            message,
            user_message,
            error_code=ErrorCode.CONFIGURATION_ERROR
        )


class FileSystemError(CapcatError):
    """Raised when file system operations fail (read, write, mkdir, unlink)."""

    def __init__(
        self, operation: str, path: str, original_error: Exception = None
    ):
        """Create a FileSystemError.

        Args:
            operation: Verb describing the failed operation (e.g. ``"write"``).
            path: Filesystem path where the operation failed.
            original_error: The underlying ``OSError`` or ``IOError``.
        """
        message = (
            f"File system error during {operation} at "
            f"{path}: {original_error}"
        )
        user_message = (
            f"Unable to {operation} at '{path}'. "
            "Please check permissions and disk space."
        )
        super().__init__(
            message,
            user_message,
            original_error,
            ErrorCode.FILESYSTEM_ERROR
        )
        self.operation = operation
        self.path = path


class ParsingError(CapcatError):
    """Raised when HTML or feed content cannot be parsed (structure changed, truncated, etc.)."""

    def __init__(self, url: str, reason: str):
        """Create a ParsingError.

        Args:
            url: The URL whose content failed to parse.
            reason: Technical description of the parse failure.
        """
        message = f"Parsing error for {url}: {reason}"
        user_message = (
            f"Could not parse content from {url}. "
            "The page structure may have changed."
        )
        super().__init__(
            message,
            user_message,
            error_code=ErrorCode.PARSING_ERROR
        )
        self.url = url


class ValidationError(CapcatError):
    """Raised when input validation fails (invalid URL, bad config value, etc.)."""

    def __init__(self, field: str, value: str, requirement: str):
        """Create a ValidationError.

        Args:
            field: Name of the field that failed validation (e.g. ``"url"``).
            value: The invalid value that was provided.
            requirement: Description of what the value should satisfy.
        """
        message = (
            f"Validation error for {field}='{value}': {requirement}"
        )
        user_message = f"Invalid {field}: {requirement}"
        super().__init__(
            message,
            user_message,
            error_code=ErrorCode.VALIDATION_ERROR
        )
        self.field = field
        self.value = value

class InvalidFeedError(CapcatError):
    """Raised when a URL does not point to a valid RSS/Atom feed."""

    def __init__(
        self,
        url: str,
        reason: str = "Not a valid RSS/Atom feed.",
    ):
        """Create an InvalidFeedError.

        Args:
            url: The URL that was tested as a feed.
            reason: Optional description of why it is not a valid feed.
        """
        message = f"Invalid feed at {url}: {reason}"
        user_message = (
            f"The content at {url} doesn't appear to be "
            "a valid RSS or Atom feed."
        )
        super().__init__(
            message,
            user_message,
            error_code=ErrorCode.VALIDATION_ERROR
        )
        self.url = url