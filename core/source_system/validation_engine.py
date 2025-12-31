#!/usr/bin/env python3
"""
Enhanced configuration validation engine for the source system.
Provides comprehensive validation rules and automated testing.
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from ..logging_config import get_logger
from .base_source import SourceConfig


class ValidationResult:
    """Result of a validation check."""

    def __init__(
        self,
        is_valid: bool,
        message: str,
        severity: str = "error",
        category: str = "general",
    ):
        self.is_valid = is_valid
        self.message = message
        self.severity = severity  # "error", "warning", "info"
        self.category = category  # "network", "config", "selectors", "general"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.category}: {self.message}"


class ValidationEngine:
    """
    Comprehensive validation engine for source configurations.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.session = requests.Session()

        # Configure session with reasonable defaults
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; Capcat-Validator/1.0)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

    def validate_config(
        self, config: SourceConfig, deep_validation: bool = False
    ) -> List[ValidationResult]:
        """
        Validate a source configuration.

        Args:
            config: Source configuration to validate
            deep_validation: Whether to perform deep validation (network requests)

        Returns:
            List of validation results
        """
        results = []

        # Basic validation
        results.extend(self._validate_basic_fields(config))
        results.extend(self._validate_url_format(config))
        results.extend(self._validate_timing_settings(config))

        # Source type specific validation
        if config.custom_config:
            if self._is_config_driven_source(config):
                results.extend(self._validate_config_driven_source(config))
            else:
                results.extend(self._validate_custom_source(config))

        # Deep validation (optional)
        if deep_validation:
            results.extend(self._validate_network_connectivity(config))
            results.extend(self._validate_selectors(config))

        return results

    def _validate_basic_fields(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate basic required fields."""
        results = []

        # Name validation
        if not config.name:
            results.append(
                ValidationResult(
                    False, "Source name is required", "error", "config"
                )
            )
        elif not re.match(r"^[a-zA-Z0-9_]+$", config.name):
            results.append(
                ValidationResult(
                    False,
                    "Source name must contain only letters, numbers, and underscores",
                    "error",
                    "config",
                )
            )

        # Display name validation
        if not config.display_name:
            results.append(
                ValidationResult(
                    False, "Display name is required", "error", "config"
                )
            )
        elif len(config.display_name) > 100:
            results.append(
                ValidationResult(
                    False,
                    "Display name must be 100 characters or less",
                    "warning",
                    "config",
                )
            )

        # Category validation
        valid_categories = [
            "tech",
            "news",
            "science",
            "business",
            "aggregator",
            "general",
            "test",
        ]
        if config.category not in valid_categories:
            results.append(
                ValidationResult(
                    False,
                    f"Category '{config.category}' is not recognized. Valid categories: {', '.join(valid_categories)}",
                    "warning",
                    "config",
                )
            )

        return results

    def _validate_url_format(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate URL format and structure."""
        results = []

        if not config.base_url:
            results.append(
                ValidationResult(
                    False, "Base URL is required", "error", "config"
                )
            )
            return results

        try:
            parsed = urlparse(config.base_url)

            # Scheme validation
            if not parsed.scheme:
                results.append(
                    ValidationResult(
                        False,
                        "Base URL must include scheme (http:// or https://)",
                        "error",
                        "config",
                    )
                )
            elif parsed.scheme not in ["http", "https"]:
                results.append(
                    ValidationResult(
                        False,
                        "Base URL must use http:// or https://",
                        "error",
                        "config",
                    )
                )

            # Domain validation
            if not parsed.netloc:
                results.append(
                    ValidationResult(
                        False,
                        "Base URL must include a valid domain",
                        "error",
                        "config",
                    )
                )
            elif "." not in parsed.netloc:
                results.append(
                    ValidationResult(
                        False,
                        "Base URL domain appears invalid",
                        "warning",
                        "config",
                    )
                )

            # Path validation
            if parsed.path and parsed.path.endswith("/"):
                results.append(
                    ValidationResult(
                        True,
                        "Base URL ends with '/'. This is usually correct for news sites.",
                        "info",
                        "config",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    False, f"Invalid URL format: {e}", "error", "config"
                )
            )

        return results

    def _validate_timing_settings(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate timeout and rate limiting settings."""
        results = []

        # Timeout validation
        if config.timeout <= 0:
            results.append(
                ValidationResult(
                    False, "Timeout must be positive", "error", "config"
                )
            )
        elif config.timeout < 5:
            results.append(
                ValidationResult(
                    True,
                    f"Timeout of {config.timeout}s is quite short, may cause failures",
                    "warning",
                    "config",
                )
            )
        elif config.timeout > 60:
            results.append(
                ValidationResult(
                    True,
                    f"Timeout of {config.timeout}s is very long, may slow down processing",
                    "warning",
                    "config",
                )
            )

        # Rate limit validation
        if config.rate_limit < 0:
            results.append(
                ValidationResult(
                    False, "Rate limit must be non-negative", "error", "config"
                )
            )
        elif config.rate_limit == 0:
            results.append(
                ValidationResult(
                    True,
                    "Rate limit of 0 means no rate limiting - use with caution",
                    "warning",
                    "config",
                )
            )
        elif config.rate_limit > 10:
            results.append(
                ValidationResult(
                    True,
                    f"Rate limit of {config.rate_limit} requests/second is very aggressive",
                    "warning",
                    "config",
                )
            )

        return results

    def _is_config_driven_source(self, config: SourceConfig) -> bool:
        """Check if this is a config-driven source."""
        return (
            "article_selectors" in config.custom_config
            or "content_selectors" in config.custom_config
        )

    def _validate_config_driven_source(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate config-driven source specific settings."""
        results = []
        custom_config = config.custom_config

        # Required fields for config-driven sources
        if not custom_config.get("article_selectors"):
            results.append(
                ValidationResult(
                    False,
                    "Config-driven sources require 'article_selectors'",
                    "error",
                    "selectors",
                )
            )
        else:
            results.extend(
                self._validate_css_selectors(
                    custom_config["article_selectors"], "article_selectors"
                )
            )

        if not custom_config.get("content_selectors"):
            results.append(
                ValidationResult(
                    False,
                    "Config-driven sources require 'content_selectors'",
                    "error",
                    "selectors",
                )
            )
        else:
            results.extend(
                self._validate_css_selectors(
                    custom_config["content_selectors"], "content_selectors"
                )
            )

        # Optional but recommended fields
        if not custom_config.get("skip_patterns"):
            results.append(
                ValidationResult(
                    True,
                    "No skip_patterns defined. Consider adding patterns to avoid unwanted URLs",
                    "info",
                    "config",
                )
            )

        return results

    def _validate_custom_source(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate custom source configuration."""
        results = []

        # Custom sources should have minimal required configuration
        # since their logic is in code
        results.append(
            ValidationResult(
                True,
                f"Custom source '{config.name}' - validation will depend on implementation",
                "info",
                "general",
            )
        )

        return results

    def _validate_css_selectors(
        self, selectors: List[str], field_name: str
    ) -> List[ValidationResult]:
        """Validate CSS selector syntax."""
        results = []

        if not isinstance(selectors, list):
            results.append(
                ValidationResult(
                    False, f"{field_name} must be a list", "error", "selectors"
                )
            )
            return results

        if not selectors:
            results.append(
                ValidationResult(
                    False,
                    f"{field_name} cannot be empty",
                    "error",
                    "selectors",
                )
            )
            return results

        for i, selector in enumerate(selectors):
            if not isinstance(selector, str):
                results.append(
                    ValidationResult(
                        False,
                        f"{field_name}[{i}] must be a string",
                        "error",
                        "selectors",
                    )
                )
                continue

            if not selector.strip():
                results.append(
                    ValidationResult(
                        False,
                        f"{field_name}[{i}] cannot be empty or whitespace",
                        "error",
                        "selectors",
                    )
                )
                continue

            # Basic CSS selector validation
            try:
                # Try to parse with BeautifulSoup to catch obvious syntax errors
                soup = BeautifulSoup("<div></div>", "html.parser")
                soup.select(selector)
            except Exception as e:
                results.append(
                    ValidationResult(
                        False,
                        f"{field_name}[{i}] has invalid CSS selector syntax: {selector} ({e})",
                        "error",
                        "selectors",
                    )
                )

        return results

    def _validate_network_connectivity(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate network connectivity to the source."""
        results = []

        try:
            self.logger.debug(f"Testing connectivity to {config.base_url}")
            start_time = time.time()

            response = self.session.get(
                config.base_url, timeout=config.timeout, allow_redirects=True
            )

            response_time = time.time() - start_time

            # Check response status
            if response.status_code == 200:
                results.append(
                    ValidationResult(
                        True,
                        f"Successfully connected to {config.base_url} ({response_time:.2f}s)",
                        "info",
                        "network",
                    )
                )
            elif response.status_code in [301, 302, 303, 307, 308]:
                results.append(
                    ValidationResult(
                        True,
                        f"URL redirects (status {response.status_code}). Final URL: {response.url}",
                        "warning",
                        "network",
                    )
                )
            elif response.status_code == 403:
                results.append(
                    ValidationResult(
                        False,
                        f"Access forbidden (403). Site may block automated requests",
                        "warning",
                        "network",
                    )
                )
            elif response.status_code == 404:
                results.append(
                    ValidationResult(
                        False,
                        f"URL not found (404): {config.base_url}",
                        "error",
                        "network",
                    )
                )
            elif response.status_code >= 500:
                results.append(
                    ValidationResult(
                        False,
                        f"Server error (status {response.status_code}). Site may be down",
                        "warning",
                        "network",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        False,
                        f"Unexpected response status: {response.status_code}",
                        "warning",
                        "network",
                    )
                )

            # Check response time
            if response_time > config.timeout * 0.8:
                results.append(
                    ValidationResult(
                        True,
                        f"Response time ({response_time:.2f}s) is close to timeout ({config.timeout}s)",
                        "warning",
                        "network",
                    )
                )

            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                results.append(
                    ValidationResult(
                        True,
                        f"Content-Type is '{content_type}', expected HTML",
                        "warning",
                        "network",
                    )
                )

        except requests.exceptions.Timeout:
            results.append(
                ValidationResult(
                    False,
                    f"Connection timeout after {config.timeout}s",
                    "error",
                    "network",
                )
            )
        except requests.exceptions.ConnectionError:
            results.append(
                ValidationResult(
                    False,
                    f"Cannot connect to {config.base_url}. Check URL or network connectivity",
                    "error",
                    "network",
                )
            )
        except Exception as e:
            results.append(
                ValidationResult(
                    False,
                    f"Network validation failed: {e}",
                    "warning",
                    "network",
                )
            )

        return results

    def _validate_selectors(
        self, config: SourceConfig
    ) -> List[ValidationResult]:
        """Validate selectors against actual page content."""
        results = []

        if not self._is_config_driven_source(config):
            return results

        try:
            # Fetch the page
            response = self.session.get(
                config.base_url, timeout=config.timeout
            )
            if response.status_code != 200:
                results.append(
                    ValidationResult(
                        True,
                        "Cannot validate selectors - page not accessible",
                        "warning",
                        "selectors",
                    )
                )
                return results

            soup = BeautifulSoup(response.text, "html.parser")
            custom_config = config.custom_config

            # Test article selectors
            article_selectors = custom_config.get("article_selectors", [])
            total_article_matches = 0

            for selector in article_selectors:
                try:
                    matches = soup.select(selector)
                    total_article_matches += len(matches)

                    if not matches:
                        results.append(
                            ValidationResult(
                                True,
                                f"Article selector '{selector}' found no matches",
                                "warning",
                                "selectors",
                            )
                        )
                    elif len(matches) > 50:
                        results.append(
                            ValidationResult(
                                True,
                                f"Article selector '{selector}' found {len(matches)} matches (may be too broad)",
                                "warning",
                                "selectors",
                            )
                        )

                except Exception as e:
                    results.append(
                        ValidationResult(
                            False,
                            f"Error testing article selector '{selector}': {e}",
                            "error",
                            "selectors",
                        )
                    )

            if total_article_matches == 0:
                results.append(
                    ValidationResult(
                        False,
                        "No article selectors found any matches. Check selectors or page structure",
                        "error",
                        "selectors",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        True,
                        f"Article selectors found {total_article_matches} total matches",
                        "info",
                        "selectors",
                    )
                )

            # Test content selectors on first article link if available
            if total_article_matches > 0:
                first_link = None
                for selector in article_selectors:
                    links = soup.select(selector)
                    if links:
                        href = links[0].get("href", "")
                        if href:
                            if href.startswith("/"):
                                first_link = config.base_url.rstrip("/") + href
                            elif href.startswith("http"):
                                first_link = href
                            break

                if first_link:
                    results.extend(
                        self._validate_content_selectors_on_page(
                            first_link,
                            config.custom_config.get("content_selectors", []),
                        )
                    )

        except Exception as e:
            results.append(
                ValidationResult(
                    True,
                    f"Could not validate selectors against page content: {e}",
                    "warning",
                    "selectors",
                )
            )

        return results

    def _validate_content_selectors_on_page(
        self, url: str, content_selectors: List[str]
    ) -> List[ValidationResult]:
        """Validate content selectors on a specific article page."""
        results = []

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return [
                    ValidationResult(
                        True,
                        f"Cannot test content selectors - article page not accessible: {url}",
                        "warning",
                        "selectors",
                    )
                ]

            soup = BeautifulSoup(response.text, "html.parser")
            total_content_matches = 0

            for selector in content_selectors:
                try:
                    matches = soup.select(selector)
                    if matches:
                        # Check if the content is substantial
                        content = " ".join(
                            match.get_text().strip() for match in matches
                        )
                        total_content_matches += len(content)

                        if len(content) < 100:
                            results.append(
                                ValidationResult(
                                    True,
                                    f"Content selector '{selector}' found little content ({len(content)} chars)",
                                    "warning",
                                    "selectors",
                                )
                            )

                except Exception as e:
                    results.append(
                        ValidationResult(
                            False,
                            f"Error testing content selector '{selector}': {e}",
                            "error",
                            "selectors",
                        )
                    )

            if total_content_matches == 0:
                results.append(
                    ValidationResult(
                        False,
                        "Content selectors found no content on sample article page",
                        "error",
                        "selectors",
                    )
                )
            elif total_content_matches < 500:
                results.append(
                    ValidationResult(
                        True,
                        f"Content selectors found limited content ({total_content_matches} chars)",
                        "warning",
                        "selectors",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        True,
                        f"Content selectors found substantial content ({total_content_matches} chars)",
                        "info",
                        "selectors",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    True,
                    f"Could not validate content selectors: {e}",
                    "warning",
                    "selectors",
                )
            )

        return results

    def validate_all_sources(
        self,
        source_configs: Dict[str, SourceConfig],
        deep_validation: bool = False,
    ) -> Dict[str, List[ValidationResult]]:
        """
        Validate all source configurations.

        Args:
            source_configs: Dictionary of source configurations
            deep_validation: Whether to perform deep validation

        Returns:
            Dictionary mapping source names to validation results
        """
        results = {}

        self.logger.info(
            f"Validating {len(source_configs)} source configurations "
            f"(deep_validation={deep_validation})"
        )

        for source_name, config in source_configs.items():
            self.logger.debug(f"Validating source: {source_name}")
            results[source_name] = self.validate_config(
                config, deep_validation
            )

        return results

    def generate_validation_report(
        self, validation_results: Dict[str, List[ValidationResult]]
    ) -> str:
        """Generate a human-readable validation report."""
        report = []
        report.append("🔍 Source Configuration Validation Report")
        report.append("=" * 60)

        # Summary statistics
        total_sources = len(validation_results)
        sources_with_errors = sum(
            1
            for results in validation_results.values()
            if any(not r.is_valid and r.severity == "error" for r in results)
        )
        sources_with_warnings = sum(
            1
            for results in validation_results.values()
            if any(not r.is_valid and r.severity == "warning" for r in results)
        )

        report.append(f"Total Sources: {total_sources}")
        report.append(f"Sources with Errors: {sources_with_errors}")
        report.append(f"Sources with Warnings: {sources_with_warnings}")
        report.append(
            f"Sources Validated Successfully: {total_sources - sources_with_errors}"
        )
        report.append("")

        # Detailed results
        for source_name, results in validation_results.items():
            errors = [
                r for r in results if not r.is_valid and r.severity == "error"
            ]
            warnings = [
                r
                for r in results
                if not r.is_valid and r.severity == "warning"
            ]
            info = [r for r in results if r.is_valid and r.severity == "info"]

            if errors or warnings:
                report.append(f"📋 {source_name}:")

                for error in errors:
                    report.append(f"  ❌ {error.message}")

                for warning in warnings:
                    report.append(f"  ⚠️  {warning.message}")

                if info:
                    for i in info[:2]:  # Limit info messages
                        report.append(f"  ℹ️  {i.message}")

                report.append("")

        # Summary of common issues
        all_results = [
            r for results in validation_results.values() for r in results
        ]
        common_errors = {}
        common_warnings = {}

        for result in all_results:
            if not result.is_valid:
                # Categorize by message prefix
                category = (
                    result.message.split(":")[0]
                    if ":" in result.message
                    else result.message
                )
                if result.severity == "error":
                    common_errors[category] = (
                        common_errors.get(category, 0) + 1
                    )
                elif result.severity == "warning":
                    common_warnings[category] = (
                        common_warnings.get(category, 0) + 1
                    )

        if common_errors or common_warnings:
            report.append("📊 Common Issues:")
            for error, count in sorted(
                common_errors.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                report.append(f"  ❌ {error}: {count} sources")
            for warning, count in sorted(
                common_warnings.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                report.append(f"  ⚠️  {warning}: {count} sources")

        return "\n".join(report)
