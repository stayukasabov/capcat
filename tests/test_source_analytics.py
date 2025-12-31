"""
Tests for source analytics and usage tracking.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
import json

from core.source_system.source_analytics import (
    SourceAnalytics,
    SourceUsageStats,
    AnalyticsReporter
)


class TestSourceAnalytics:
    """Test analytics tracking functionality."""

    @pytest.fixture
    def temp_analytics_file(self, tmp_path):
        """Create temporary analytics file."""
        return tmp_path / "analytics.json"

    @pytest.fixture
    def analytics(self, temp_analytics_file):
        """Create SourceAnalytics instance."""
        return SourceAnalytics(temp_analytics_file)

    def test_record_successful_fetch(self, analytics):
        """Test recording a successful fetch."""
        analytics.record_fetch("test1", True, 10)

        stats = analytics.get_source_stats("test1")
        assert stats.total_fetches == 1
        assert stats.successful_fetches == 1
        assert stats.failed_fetches == 0
        assert stats.articles_fetched == 10

    def test_record_failed_fetch(self, analytics):
        """Test recording a failed fetch."""
        analytics.record_fetch("test1", False, 0)

        stats = analytics.get_source_stats("test1")
        assert stats.total_fetches == 1
        assert stats.successful_fetches == 0
        assert stats.failed_fetches == 1
        assert stats.articles_fetched == 0

    def test_multiple_fetches(self, analytics):
        """Test multiple fetch records."""
        analytics.record_fetch("test1", True, 10)
        analytics.record_fetch("test1", True, 15)
        analytics.record_fetch("test1", False, 0)

        stats = analytics.get_source_stats("test1")
        assert stats.total_fetches == 3
        assert stats.successful_fetches == 2
        assert stats.failed_fetches == 1
        assert stats.articles_fetched == 25
        assert stats.avg_articles_per_fetch == 8.3  # 25/3 rounded

    def test_fetch_history_limited(self, analytics):
        """Test that fetch history is limited to 30 records."""
        for i in range(50):
            analytics.record_fetch("test1", True, i)

        data = analytics._data["test1"]
        assert len(data["fetch_history"]) == 30

    def test_get_unused_sources(self, analytics, temp_analytics_file):
        """Test identifying unused sources."""
        # Create old fetch
        old_date = (datetime.now() - timedelta(days=60)).isoformat()

        # Manually create old data
        analytics._data = {
            "test1": {
                "total_fetches": 1,
                "successful_fetches": 1,
                "failed_fetches": 0,
                "articles_fetched": 10,
                "last_fetch_date": old_date,
                "last_success_date": old_date,
                "fetch_history": []
            },
            "test2": {
                "total_fetches": 0,
                "successful_fetches": 0,
                "failed_fetches": 0,
                "articles_fetched": 0,
                "last_fetch_date": None,
                "last_success_date": None,
                "fetch_history": []
            }
        }
        analytics._save_data()

        unused = analytics.get_unused_sources(["test1", "test2", "test3"], days_threshold=30)

        assert "test1" in unused  # 60 days old > 30 threshold
        assert "test2" in unused  # Never used
        assert "test3" in unused  # Not in analytics (never used)

    def test_get_low_performing_sources(self, analytics):
        """Test identifying low performing sources."""
        # test1: 1 success out of 5 fetches = 20% success rate
        for i in range(5):
            analytics.record_fetch("test1", i == 0, 10 if i == 0 else 0)

        # test2: 4 successes out of 5 fetches = 80% success rate
        for i in range(5):
            analytics.record_fetch("test2", i != 0, 10)

        low_performers = analytics.get_low_performing_sources(
            ["test1", "test2"],
            min_success_rate=0.5
        )

        # test1 has 20% success rate (< 50% threshold)
        assert len(low_performers) == 1
        assert low_performers[0][0] == "test1"
        assert low_performers[0][1] < 0.5

    def test_frequency_calculation_daily(self, analytics):
        """Test daily frequency calculation."""
        # Record fetches 1 day apart
        for i in range(5):
            analytics.record_fetch("test1", True, 10)

        stats = analytics.get_source_stats("test1")
        # With recent fetches, should be classified as active
        assert stats.fetch_frequency in ["daily", "weekly"]

    def test_persistence(self, analytics, temp_analytics_file):
        """Test that analytics persist across instances."""
        # Record data
        analytics.record_fetch("test1", True, 10)

        # Create new instance with same file
        analytics2 = SourceAnalytics(temp_analytics_file)
        stats = analytics2.get_source_stats("test1")

        assert stats.total_fetches == 1
        assert stats.articles_fetched == 10

    def test_get_all_stats(self, analytics):
        """Test getting stats for all sources."""
        analytics.record_fetch("test1", True, 10)
        analytics.record_fetch("test2", True, 20)
        analytics.record_fetch("test3", True, 5)

        source_names = {
            "test1": "Test One",
            "test2": "Test Two",
            "test3": "Test Three"
        }

        all_stats = analytics.get_all_stats(source_names)

        assert len(all_stats) == 3
        # Should be sorted by total fetches (all have 1, so by display name)
        assert all_stats[0].source_id in source_names


class TestAnalyticsReporter:
    """Test analytics reporting functionality."""

    def test_format_stats(self):
        """Test formatting source stats."""
        stats = SourceUsageStats(
            source_id="test1",
            display_name="Test Source",
            total_fetches=10,
            successful_fetches=8,
            failed_fetches=2,
            last_fetch_date="2025-01-18T10:00:00",
            last_success_date="2025-01-18T10:00:00",
            articles_fetched=100,
            avg_articles_per_fetch=10.0,
            days_since_last_use=5,
            fetch_frequency="daily"
        )

        formatted = AnalyticsReporter.format_stats(stats)

        assert "Test Source" in formatted
        assert "10" in formatted  # Total fetches
        assert "80.0%" in formatted  # Success rate
        assert "daily" in formatted

    def test_removal_recommendation_never_used(self):
        """Test recommendation for never-used source."""
        stats = SourceUsageStats(
            source_id="test1",
            display_name="Test",
            total_fetches=0,
            successful_fetches=0,
            failed_fetches=0,
            last_fetch_date=None,
            last_success_date=None,
            articles_fetched=0,
            avg_articles_per_fetch=0.0,
            days_since_last_use=None,
            fetch_frequency="never"
        )

        recommendation = AnalyticsReporter.format_removal_recommendation(stats)
        assert "[RECOMMENDED]" in recommendation
        assert "Never used" in recommendation

    def test_removal_recommendation_old_source(self):
        """Test recommendation for source not used in 90+ days."""
        stats = SourceUsageStats(
            source_id="test1",
            display_name="Test",
            total_fetches=5,
            successful_fetches=5,
            failed_fetches=0,
            last_fetch_date="2024-01-01T00:00:00",
            last_success_date="2024-01-01T00:00:00",
            articles_fetched=50,
            avg_articles_per_fetch=10.0,
            days_since_last_use=365,
            fetch_frequency="rarely"
        )

        recommendation = AnalyticsReporter.format_removal_recommendation(stats)
        assert "[RECOMMENDED]" in recommendation
        assert "90+" in recommendation

    def test_removal_recommendation_low_success(self):
        """Test recommendation for low success rate."""
        stats = SourceUsageStats(
            source_id="test1",
            display_name="Test",
            total_fetches=10,
            successful_fetches=2,  # 20% success rate
            failed_fetches=8,
            last_fetch_date="2025-01-18T00:00:00",
            last_success_date="2025-01-18T00:00:00",
            articles_fetched=20,
            avg_articles_per_fetch=2.0,
            days_since_last_use=1,
            fetch_frequency="daily"
        )

        recommendation = AnalyticsReporter.format_removal_recommendation(stats)
        assert "[WARNING]" in recommendation
        assert "success rate" in recommendation

    def test_removal_recommendation_active(self):
        """Test recommendation for active source."""
        stats = SourceUsageStats(
            source_id="test1",
            display_name="Test",
            total_fetches=50,
            successful_fetches=48,
            failed_fetches=2,
            last_fetch_date="2025-01-18T00:00:00",
            last_success_date="2025-01-18T00:00:00",
            articles_fetched=500,
            avg_articles_per_fetch=10.0,
            days_since_last_use=1,
            fetch_frequency="daily"
        )

        recommendation = AnalyticsReporter.format_removal_recommendation(stats)
        assert "[ACTIVE]" in recommendation


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.source_system.source_analytics'])