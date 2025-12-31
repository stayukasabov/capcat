"""
Source usage analytics and statistics.
Tracks source usage patterns for informed removal decisions.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from core.logging_config import get_logger


@dataclass
class SourceUsageStats:
    """Statistics about source usage."""
    source_id: str
    display_name: str
    total_fetches: int
    successful_fetches: int
    failed_fetches: int
    last_fetch_date: Optional[str]
    last_success_date: Optional[str]
    articles_fetched: int
    avg_articles_per_fetch: float
    days_since_last_use: Optional[int]
    fetch_frequency: str  # "daily", "weekly", "monthly", "rarely", "never"


class SourceAnalytics:
    """
    Tracks and analyzes source usage patterns.
    Helps users make informed decisions about source removal.
    """

    def __init__(self, analytics_file: Optional[Path] = None):
        """
        Initialize source analytics.

        Args:
            analytics_file: Path to analytics data file
        """
        if analytics_file is None:
            import cli
            app_root = Path(cli.__file__).parent
            analytics_file = app_root.parent / ".capcat_analytics" / "usage.json"

        self._analytics_file = Path(analytics_file)
        self._analytics_file.parent.mkdir(parents=True, exist_ok=True)
        self._logger = get_logger(__name__)
        self._data = self._load_data()

    def record_fetch(
        self,
        source_id: str,
        success: bool,
        articles_count: int = 0
    ) -> None:
        """
        Record a fetch operation for analytics.

        Args:
            source_id: Source identifier
            success: Whether fetch was successful
            articles_count: Number of articles fetched
        """
        if source_id not in self._data:
            self._data[source_id] = {
                "total_fetches": 0,
                "successful_fetches": 0,
                "failed_fetches": 0,
                "articles_fetched": 0,
                "last_fetch_date": None,
                "last_success_date": None,
                "fetch_history": []
            }

        entry = self._data[source_id]
        entry["total_fetches"] += 1
        entry["last_fetch_date"] = datetime.now().isoformat()

        if success:
            entry["successful_fetches"] += 1
            entry["articles_fetched"] += articles_count
            entry["last_success_date"] = datetime.now().isoformat()

        else:
            entry["failed_fetches"] += 1

        # Keep last 30 fetch records
        entry["fetch_history"].append({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "articles": articles_count
        })
        entry["fetch_history"] = entry["fetch_history"][-30:]

        self._save_data()

    def get_source_stats(self, source_id: str, display_name: str = None) -> SourceUsageStats:
        """
        Get usage statistics for a source.

        Args:
            source_id: Source identifier
            display_name: Display name (optional)

        Returns:
            SourceUsageStats object
        """
        data = self._data.get(source_id, {
            "total_fetches": 0,
            "successful_fetches": 0,
            "failed_fetches": 0,
            "articles_fetched": 0,
            "last_fetch_date": None,
            "last_success_date": None
        })

        # Calculate derived stats
        total_fetches = data["total_fetches"]
        articles_fetched = data["articles_fetched"]
        avg_articles = articles_fetched / total_fetches if total_fetches > 0 else 0.0

        # Calculate days since last use
        days_since_last_use = None
        if data["last_fetch_date"]:
            last_date = datetime.fromisoformat(data["last_fetch_date"])
            days_since_last_use = (datetime.now() - last_date).days

        # Determine fetch frequency
        frequency = self._calculate_frequency(source_id, days_since_last_use)

        return SourceUsageStats(
            source_id=source_id,
            display_name=display_name or source_id,
            total_fetches=data["total_fetches"],
            successful_fetches=data["successful_fetches"],
            failed_fetches=data["failed_fetches"],
            last_fetch_date=data["last_fetch_date"],
            last_success_date=data["last_success_date"],
            articles_fetched=articles_fetched,
            avg_articles_per_fetch=round(avg_articles, 1),
            days_since_last_use=days_since_last_use,
            fetch_frequency=frequency
        )

    def get_all_stats(self, source_names: Dict[str, str]) -> List[SourceUsageStats]:
        """
        Get statistics for all tracked sources.

        Args:
            source_names: Mapping of source_id to display_name

        Returns:
            List of SourceUsageStats objects
        """
        stats = []
        for source_id, display_name in source_names.items():
            stats.append(self.get_source_stats(source_id, display_name))

        return sorted(stats, key=lambda s: s.total_fetches, reverse=True)

    def get_unused_sources(
        self,
        all_source_ids: List[str],
        days_threshold: int = 30
    ) -> List[str]:
        """
        Get sources that haven't been used recently.

        Args:
            all_source_ids: List of all available source IDs
            days_threshold: Days without use to consider unused

        Returns:
            List of unused source IDs
        """
        unused = []

        for source_id in all_source_ids:
            data = self._data.get(source_id)

            # Never used
            if not data or data["total_fetches"] == 0:
                unused.append(source_id)
                continue

            # Not used recently
            if data["last_fetch_date"]:
                last_date = datetime.fromisoformat(data["last_fetch_date"])
                days_since = (datetime.now() - last_date).days
                if days_since > days_threshold:
                    unused.append(source_id)

        return unused

    def get_low_performing_sources(
        self,
        all_source_ids: List[str],
        min_success_rate: float = 0.5
    ) -> List[tuple[str, float]]:
        """
        Get sources with low success rates.

        Args:
            all_source_ids: List of all available source IDs
            min_success_rate: Minimum acceptable success rate (0.0-1.0)

        Returns:
            List of tuples (source_id, success_rate)
        """
        low_performers = []

        for source_id in all_source_ids:
            data = self._data.get(source_id)

            if not data or data["total_fetches"] < 3:  # Need minimum sample
                continue

            success_rate = data["successful_fetches"] / data["total_fetches"]
            if success_rate < min_success_rate:
                low_performers.append((source_id, success_rate))

        return sorted(low_performers, key=lambda x: x[1])

    def _calculate_frequency(self, source_id: str, days_since_last: Optional[int]) -> str:
        """Calculate fetch frequency category."""
        data = self._data.get(source_id, {})
        history = data.get("fetch_history", [])

        if not history:
            return "never"

        if days_since_last is None:
            return "never"

        # Calculate average days between fetches
        if len(history) >= 2:
            dates = [datetime.fromisoformat(h["timestamp"]) for h in history[-10:]]
            if len(dates) >= 2:
                intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                avg_interval = sum(intervals) / len(intervals)

                if avg_interval <= 1.5:
                    return "daily"
                elif avg_interval <= 7:
                    return "weekly"
                elif avg_interval <= 30:
                    return "monthly"

        # Fallback based on last use
        if days_since_last <= 7:
            return "weekly"
        elif days_since_last <= 30:
            return "monthly"
        else:
            return "rarely"

    def _load_data(self) -> Dict[str, Any]:
        """Load analytics data from file."""
        if not self._analytics_file.exists():
            return {}

        try:
            with open(self._analytics_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self._logger.warning(f"Failed to load analytics: {e}")
            return {}

    def _save_data(self) -> None:
        """Save analytics data to file."""
        try:
            with open(self._analytics_file, 'w') as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            self._logger.error(f"Failed to save analytics: {e}")


class AnalyticsReporter:
    """Generates human-readable analytics reports."""

    @staticmethod
    def format_stats(stats: SourceUsageStats) -> str:
        """Format source stats as readable text."""
        lines = [
            f"Source: {stats.display_name} ({stats.source_id})",
            f"  Total fetches: {stats.total_fetches}",
            f"  Success rate: {stats.successful_fetches}/{stats.total_fetches} ({stats.successful_fetches/stats.total_fetches*100 if stats.total_fetches > 0 else 0:.1f}%)",
            f"  Articles fetched: {stats.articles_fetched} (avg: {stats.avg_articles_per_fetch}/fetch)",
            f"  Frequency: {stats.fetch_frequency}",
        ]

        if stats.last_fetch_date:
            lines.append(f"  Last used: {stats.days_since_last_use} days ago")
        else:
            lines.append("  Last used: Never")

        return "\n".join(lines)

    @staticmethod
    def format_removal_recommendation(stats: SourceUsageStats) -> str:
        """Generate removal recommendation based on stats."""
        if stats.total_fetches == 0:
            return "[RECOMMENDED] Never used"

        if stats.days_since_last_use and stats.days_since_last_use > 90:
            return "[RECOMMENDED] Not used in 90+ days"

        success_rate = stats.successful_fetches / stats.total_fetches if stats.total_fetches > 0 else 0
        if success_rate < 0.3:
            return f"[WARNING] Low success rate ({success_rate*100:.1f}%)"

        if stats.fetch_frequency == "rarely":
            return "[CONSIDER] Rarely used"

        return "[ACTIVE] Regular use"