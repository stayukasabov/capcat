#!/usr/bin/env python3
"""
Source factory for creating and managing news source instances.
Provides a high-level interface for source instantiation and management.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

import requests

from ..logging_config import get_logger
from ..session_pool import get_global_session
from .base_source import BaseSource, SourceConfig, SourceError
from .performance_monitor import get_performance_monitor
from .source_registry import SourceRegistry, get_source_registry


class SourceFactory:
    """
    Factory for creating and managing news source instances.

    Provides high-level interface for source instantiation, batch operations,
    and source lifecycle management.
    """

    def __init__(self, registry: Optional[SourceRegistry] = None):
        """
        Initialize the source factory.

        Args:
            registry: Optional source registry (uses global registry if not provided)
        """
        self.logger = get_logger(__name__)
        self.registry = registry or get_source_registry()
        self.performance_monitor = get_performance_monitor()
        self._source_cache: Dict[str, BaseSource] = {}

    def create_source(
        self, source_name: str, use_session_pool: bool = True
    ) -> BaseSource:
        """
        Create a source instance.

        Args:
            source_name: Name of the source to create
            use_session_pool: Whether to use session pooling

        Returns:
            BaseSource instance

        Raises:
            SourceError: If source creation fails
        """
        if source_name not in self.registry.get_available_sources():
            available = ", ".join(self.registry.get_available_sources())
            raise SourceError(
                f"Unknown source '{source_name}'. Available: {available}"
            )

        # Use session pooling if requested
        session = None
        if use_session_pool:
            session = get_global_session(source_name)

        try:
            source = self.registry.get_source(source_name, session)
            self.logger.debug(f"Created source instance: {source_name}")
            return source
        except Exception as e:
            raise SourceError(f"Failed to create source '{source_name}': {e}")

    def create_sources(
        self, source_names: List[str], use_session_pool: bool = True
    ) -> Dict[str, BaseSource]:
        """
        Create multiple source instances.

        Args:
            source_names: List of source names to create
            use_session_pool: Whether to use session pooling

        Returns:
            Dictionary mapping source names to BaseSource instances

        Raises:
            SourceError: If any source creation fails
        """
        sources = {}
        failed_sources = []

        for source_name in source_names:
            try:
                sources[source_name] = self.create_source(
                    source_name, use_session_pool
                )
            except SourceError as e:
                self.logger.warning(
                    f"Failed to create source '{source_name}': {e}"
                )
                failed_sources.append(source_name)

        if failed_sources:
            raise SourceError(
                f"Failed to create sources: {', '.join(failed_sources)}"
            )

        return sources

    def get_cached_source(self, source_name: str) -> Optional[BaseSource]:
        """
        Get a cached source instance.

        Args:
            source_name: Name of the source

        Returns:
            Cached BaseSource instance or None if not cached
        """
        return self._source_cache.get(source_name)

    def cache_source(self, source_name: str, source: BaseSource):
        """
        Cache a source instance.

        Args:
            source_name: Name of the source
            source: Source instance to cache
        """
        self._source_cache[source_name] = source
        self.logger.debug(f"Cached source instance: {source_name}")

    def clear_cache(self):
        """Clear the source instance cache."""
        self._source_cache.clear()
        self.logger.debug("Source instance cache cleared")

    def validate_sources(
        self, source_names: List[str]
    ) -> Dict[str, List[str]]:
        """
        Validate multiple sources.

        Args:
            source_names: List of source names to validate

        Returns:
            Dictionary mapping source names to validation errors
        """
        validation_results = {}

        for source_name in source_names:
            try:
                source = self.create_source(source_name)
                errors = source.validate_config()
                validation_results[source_name] = errors
            except Exception as e:
                validation_results[source_name] = [
                    f"Failed to create source: {e}"
                ]

        return validation_results

    def get_sources_by_category(self, category: str) -> List[str]:
        """
        Get source names by category.

        Args:
            category: Category name

        Returns:
            List of source names in the category
        """
        return self.registry.get_sources_by_category(category)

    def get_available_sources(self) -> List[str]:
        """Get all available source names."""
        return self.registry.get_available_sources()

    def get_source_config(self, source_name: str) -> Optional[SourceConfig]:
        """
        Get source configuration.

        Args:
            source_name: Name of the source

        Returns:
            SourceConfig or None if source not found
        """
        return self.registry.get_source_config(source_name)

    def batch_discover_articles(
        self,
        source_names: List[str],
        count_per_source: int,
        max_workers: int = 4,
    ) -> Dict[str, List]:
        """
        Discover articles from multiple sources in parallel.

        Args:
            source_names: List of source names
            count_per_source: Number of articles to discover per source
            max_workers: Maximum number of worker threads

        Returns:
            Dictionary mapping source names to article lists
        """
        results = {}

        def discover_for_source(source_name: str):
            try:
                source = self.create_source(source_name)
                # Use retry-skip logic for network resilience
                articles = source.discover_articles_with_retry_skip(
                    count=count_per_source,
                    max_retries=2
                )
                # None means source was skipped after failures
                if articles is None:
                    self.logger.info(
                        f"Source '{source_name}' skipped - will continue with remaining sources"
                    )
                    return source_name, []
                return source_name, articles
            except Exception as e:
                self.logger.error(
                    f"Failed to discover articles for {source_name}: {e}"
                )
                return source_name, []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(discover_for_source, name)
                for name in source_names
            ]

            for future in futures:
                try:
                    source_name, articles = future.result(timeout=30)
                    results[source_name] = articles
                except Exception as e:
                    self.logger.error(f"Article discovery task failed: {e}")

        return results

    def test_source_connectivity(
        self, source_name: str, timeout: float = 10.0
    ) -> bool:
        """
        Test if a source is reachable.

        Args:
            source_name: Name of the source to test
            timeout: Connection timeout in seconds

        Returns:
            True if source is reachable, False otherwise
        """
        try:
            config = self.get_source_config(source_name)
            if not config:
                return False

            session = get_global_session(source_name)
            response = session.get(config.base_url, timeout=timeout)
            return response.status_code == 200

        except Exception as e:
            self.logger.debug(
                f"Connectivity test failed for {source_name}: {e}"
            )
            return False

    def get_source_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all sources.

        Returns:
            Dictionary with source statistics
        """
        stats = {
            "total_sources": len(self.get_available_sources()),
            "cached_sources": len(self._source_cache),
            "registry_stats": self.registry.get_registry_stats(),
            "sources_by_category": {},
        }

        # Group sources by category
        for source_name in self.get_available_sources():
            config = self.get_source_config(source_name)
            if config:
                category = config.category
                if category not in stats["sources_by_category"]:
                    stats["sources_by_category"][category] = []
                stats["sources_by_category"][category].append(source_name)

        return stats

    def health_check(
        self, source_names: Optional[List[str]] = None, timeout: float = 5.0
    ) -> Dict[str, bool]:
        """
        Perform health check on sources.

        Args:
            source_names: List of sources to check (all if None)
            timeout: Timeout per source check

        Returns:
            Dictionary mapping source names to health status
        """
        if source_names is None:
            source_names = self.get_available_sources()

        health_results = {}

        for source_name in source_names:
            try:
                # Test basic connectivity
                is_healthy = self.test_source_connectivity(
                    source_name, timeout
                )
                health_results[source_name] = is_healthy

                # Log result
                status = "healthy" if is_healthy else "unhealthy"
                self.logger.debug(f"Health check for {source_name}: {status}")

            except Exception as e:
                self.logger.warning(
                    f"Health check failed for {source_name}: {e}"
                )
                health_results[source_name] = False

        return health_results

    def reload_sources(self):
        """Reload all sources from the registry."""
        self.clear_cache()
        self.registry.reload_sources()
        self.logger.info("Sources reloaded")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all sources."""
        return self.performance_monitor.get_performance_summary()

    def get_source_performance(
        self, source_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific source."""
        metrics = self.performance_monitor.get_source_metrics(source_name)
        if metrics:
            from dataclasses import asdict

            return asdict(metrics)
        return None

    def generate_performance_report(self) -> str:
        """Generate a human-readable performance report."""
        return self.performance_monitor.generate_report()

    def save_performance_metrics(self):
        """Save performance metrics to disk."""
        self.performance_monitor.save_metrics()

    def __str__(self) -> str:
        """String representation of the factory."""
        return f"SourceFactory(sources={len(self.get_available_sources())}, cached={len(self._source_cache)})"


# Global factory instance
_global_factory: Optional[SourceFactory] = None


def get_source_factory() -> SourceFactory:
    """Get the global source factory instance."""
    global _global_factory
    if _global_factory is None:
        _global_factory = SourceFactory()
    return _global_factory


def reset_source_factory():
    """Reset the global source factory (useful for testing)."""
    global _global_factory
    _global_factory = None
