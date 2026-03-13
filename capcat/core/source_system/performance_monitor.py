#!/usr/bin/env python3
"""
Source performance monitoring system for the hybrid architecture.
Tracks source performance, success rates, and health metrics.
"""

import json
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..logging_config import get_logger


@dataclass
class SourceMetrics:
    """Performance metrics for a source."""

    source_name: str
    source_type: str  # 'config_driven' or 'custom'

    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # Timing metrics
    avg_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0

    # Content metrics
    articles_discovered: int = 0
    articles_fetched: int = 0
    articles_failed: int = 0

    # Error tracking
    error_types: Dict[str, int] = None
    last_error: Optional[str] = None
    last_success: Optional[str] = None

    # Health status
    is_healthy: bool = True
    last_health_check: Optional[str] = None
    consecutive_failures: int = 0

    def __post_init__(self):
        if self.error_types is None:
            self.error_types = {}

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def content_success_rate(self) -> float:
        """Calculate content fetching success rate."""
        total_content = self.articles_fetched + self.articles_failed
        if total_content == 0:
            return 0.0
        return (self.articles_fetched / total_content) * 100


class PerformanceMonitor:
    """
    Performance monitoring system for sources.
    """

    def __init__(self, metrics_file: Optional[str] = None):
        """
        Initialize performance monitor.

        Args:
            metrics_file: Path to store metrics data
        """
        self.logger = get_logger(__name__)
        self.metrics: Dict[str, SourceMetrics] = {}
        self.recent_timings: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )

        # Metrics storage
        if metrics_file is None:
            app_root = Path(__file__).parent.parent.parent
            self.metrics_file = (
                app_root / "metrics" / "source_performance.json"
            )
        else:
            self.metrics_file = Path(metrics_file)

        self.metrics_file.parent.mkdir(exist_ok=True)
        self.load_metrics()

    def start_request(self, source_name: str, source_type: str) -> float:
        """
        Start timing a request for a source.

        Args:
            source_name: Name of the source
            source_type: Type of source ('config_driven' or 'custom')

        Returns:
            Start timestamp
        """
        if source_name not in self.metrics:
            self.metrics[source_name] = SourceMetrics(
                source_name=source_name, source_type=source_type
            )

        self.metrics[source_name].total_requests += 1
        return time.time()

    def end_request(
        self,
        source_name: str,
        start_time: float,
        success: bool,
        error_type: Optional[str] = None,
    ):
        """
        End timing a request and update metrics.

        Args:
            source_name: Name of the source
            start_time: Start timestamp from start_request
            success: Whether the request was successful
            error_type: Type of error if request failed
        """
        if source_name not in self.metrics:
            self.logger.warning(
                f"No metrics initialized for source: {source_name}"
            )
            return

        # Calculate timing
        response_time = time.time() - start_time
        metrics = self.metrics[source_name]

        # Update timing metrics
        self.recent_timings[source_name].append(response_time)

        # Recalculate averages using recent timings
        recent_times = list(self.recent_timings[source_name])
        if recent_times:
            metrics.avg_response_time = sum(recent_times) / len(recent_times)
            metrics.min_response_time = min(
                metrics.min_response_time, min(recent_times)
            )
            metrics.max_response_time = max(
                metrics.max_response_time, max(recent_times)
            )

        # Update success/failure metrics
        now = datetime.now().isoformat()

        if success:
            metrics.successful_requests += 1
            metrics.last_success = now
            metrics.consecutive_failures = 0
            metrics.is_healthy = True
        else:
            metrics.failed_requests += 1
            metrics.last_error = f"{error_type}: {now}" if error_type else now
            metrics.consecutive_failures += 1

            # Mark as unhealthy after 3 consecutive failures
            if metrics.consecutive_failures >= 3:
                metrics.is_healthy = False

            # Track error types
            if error_type:
                if error_type not in metrics.error_types:
                    metrics.error_types[error_type] = 0
                metrics.error_types[error_type] += 1

        self.logger.debug(
            f"Updated metrics for {source_name}: "
            f"success_rate={metrics.success_rate:.1f}%, "
            f"avg_time={metrics.avg_response_time:.2f}s"
        )

    def record_article_discovery(self, source_name: str, count: int):
        """
        Record successful article discovery.

        Args:
            source_name: Name of the source
            count: Number of articles discovered
        """
        if source_name in self.metrics:
            self.metrics[source_name].articles_discovered += count

    def record_content_fetch(self, source_name: str, success: bool):
        """
        Record content fetching result.

        Args:
            source_name: Name of the source
            success: Whether content fetch was successful
        """
        if source_name in self.metrics:
            if success:
                self.metrics[source_name].articles_fetched += 1
            else:
                self.metrics[source_name].articles_failed += 1

    def get_source_metrics(self, source_name: str) -> Optional[SourceMetrics]:
        """Get metrics for a specific source."""
        return self.metrics.get(source_name)

    def get_all_metrics(self) -> Dict[str, SourceMetrics]:
        """Get metrics for all sources."""
        return self.metrics.copy()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all sources."""
        if not self.metrics:
            return {
                "total_sources": 0,
                "healthy_sources": 0,
                "unhealthy_sources": 0,
                "overall_success_rate": 0.0,
                "top_performers": [],
                "problem_sources": [],
            }

        healthy_sources = sum(1 for m in self.metrics.values() if m.is_healthy)
        total_requests = sum(m.total_requests for m in self.metrics.values())
        successful_requests = sum(
            m.successful_requests for m in self.metrics.values()
        )

        overall_success_rate = 0.0
        if total_requests > 0:
            overall_success_rate = (successful_requests / total_requests) * 100

        # Top performers (by success rate, minimum 5 requests)
        top_performers = sorted(
            [m for m in self.metrics.values() if m.total_requests >= 5],
            key=lambda x: x.success_rate,
            reverse=True,
        )[:5]

        # Problem sources (unhealthy or low success rate)
        problem_sources = [
            m
            for m in self.metrics.values()
            if not m.is_healthy
            or (m.total_requests >= 5 and m.success_rate < 80)
        ]

        return {
            "total_sources": len(self.metrics),
            "healthy_sources": healthy_sources,
            "unhealthy_sources": len(self.metrics) - healthy_sources,
            "overall_success_rate": overall_success_rate,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "top_performers": [
                {
                    "name": m.source_name,
                    "type": m.source_type,
                    "success_rate": m.success_rate,
                    "avg_response_time": m.avg_response_time,
                    "requests": m.total_requests,
                }
                for m in top_performers
            ],
            "problem_sources": [
                {
                    "name": m.source_name,
                    "type": m.source_type,
                    "success_rate": m.success_rate,
                    "consecutive_failures": m.consecutive_failures,
                    "last_error": m.last_error,
                }
                for m in problem_sources
            ],
        }

    def health_check_source(self, source_name: str) -> bool:
        """
        Perform health check on a specific source.

        Args:
            source_name: Name of the source to check

        Returns:
            True if source is healthy
        """
        if source_name not in self.metrics:
            return False

        metrics = self.metrics[source_name]
        now = datetime.now().isoformat()

        # Basic health criteria
        is_healthy = metrics.consecutive_failures < 3 and (
            metrics.total_requests == 0 or metrics.success_rate >= 50
        )

        metrics.is_healthy = is_healthy
        metrics.last_health_check = now

        return is_healthy

    def cleanup_old_metrics(self, days: int = 30):
        """
        Clean up old metrics data.

        Args:
            days: Number of days to keep metrics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # For now, just log the cleanup action
        # In a more sophisticated system, we would clean up old detailed logs
        self.logger.info(
            f"Cleaning up metrics older than {days} days (cutoff: {cutoff_date})"
        )

    def save_metrics(self):
        """Save metrics to file."""
        try:
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "sources": {
                    name: asdict(metrics)
                    for name, metrics in self.metrics.items()
                },
            }

            with open(self.metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)

            self.logger.debug(
                f"Saved metrics for {len(self.metrics)} sources to {self.metrics_file}"
            )

        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")

    def load_metrics(self):
        """Load metrics from file."""
        try:
            if not self.metrics_file.exists():
                self.logger.debug("No existing metrics file found")
                return

            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            if "sources" in data:
                for name, metrics_dict in data["sources"].items():
                    # Convert dict back to SourceMetrics
                    self.metrics[name] = SourceMetrics(**metrics_dict)

            self.logger.info(
                f"Loaded metrics for {len(self.metrics)} sources from {self.metrics_file}"
            )

        except Exception as e:
            self.logger.warning(f"Failed to load metrics: {e}")

    def generate_report(self) -> str:
        """Generate a human-readable performance report."""
        summary = self.get_performance_summary()

        report = []
        report.append("📊 Source Performance Report")
        report.append("=" * 50)
        report.append(f"Total Sources: {summary['total_sources']}")
        report.append(f"Healthy Sources: {summary['healthy_sources']}")
        report.append(f"Unhealthy Sources: {summary['unhealthy_sources']}")
        report.append(
            f"Overall Success Rate: {summary['overall_success_rate']:.1f}%"
        )
        report.append(f"Total Requests: {summary['total_requests']}")
        report.append("")

        if summary["top_performers"]:
            report.append("🏆 Top Performing Sources:")
            for source in summary["top_performers"]:
                report.append(
                    f"  • {source['name']} ({source['type']}): "
                    f"{source['success_rate']:.1f}% success, "
                    f"{source['avg_response_time']:.2f}s avg time, "
                    f"{source['requests']} requests"
                )
            report.append("")

        if summary["problem_sources"]:
            report.append("⚠️  Problem Sources:")
            for source in summary["problem_sources"]:
                report.append(
                    f"  • {source['name']} ({source['type']}): "
                    f"{source['success_rate']:.1f}% success, "
                    f"{source['consecutive_failures']} consecutive failures"
                )
                if source["last_error"]:
                    report.append(f"    Last error: {source['last_error']}")
            report.append("")

        # Source type breakdown
        type_breakdown = defaultdict(int)
        for metrics in self.metrics.values():
            type_breakdown[metrics.source_type] += 1

        if type_breakdown:
            report.append("📋 Source Type Breakdown:")
            for source_type, count in type_breakdown.items():
                report.append(f"  • {source_type}: {count} sources")

        return "\n".join(report)


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def reset_performance_monitor():
    """Reset the global performance monitor (useful for testing)."""
    global _performance_monitor
    _performance_monitor = None
