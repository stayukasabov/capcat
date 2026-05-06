"""Tests for EthicalScrapingManager.configure() and crawl_delay floor."""
import time
from unittest.mock import patch, MagicMock
from capcat.core.ethical_scraping import EthicalScrapingManager

# Note: tests use mock-patched sleep so they run fast (no real time.sleep calls).


class TestConfigureMethod:
    def test_configure_updates_crawl_delay(self):
        mgr = EthicalScrapingManager()
        mgr.configure(crawl_delay=2.0, robots_cache_ttl_minutes=30)
        assert mgr.crawl_delay == 2.0

    def test_configure_updates_cache_ttl(self):
        from datetime import timedelta
        mgr = EthicalScrapingManager()
        mgr.configure(crawl_delay=1.0, robots_cache_ttl_minutes=30)
        assert mgr.cache_ttl == timedelta(minutes=30)

    def test_default_crawl_delay_is_one(self):
        """self.crawl_delay must be initialized before configure() is called."""
        mgr = EthicalScrapingManager()
        assert mgr.crawl_delay == 1.0

    def test_enforce_rate_limit_crawl_delay_floor_applied(self):
        """self.crawl_delay acts as a floor: effective = max(arg, min_delay, self.crawl_delay)."""
        mgr = EthicalScrapingManager()
        mgr.configure(crawl_delay=5.0, robots_cache_ttl_minutes=15)
        # Place last_request_time in the future so the next call would need to wait
        mgr.last_request_time["example.com"] = time.time() + 4.0
        # The effective_delay should be max(0.0, 0.0, 5.0) = 5.0
        # Reserve the slot and measure what sleep_time would be - inspect via a patched sleep
        sleep_times = []
        with patch("capcat.core.ethical_scraping.time.sleep", side_effect=lambda s: sleep_times.append(s)):
            mgr.enforce_rate_limit("example.com", crawl_delay=0.0, min_delay=0.0)
        assert sleep_times, "Expected sleep to be called"
        assert sleep_times[0] >= 4.5  # slot was 4s in future + floor = still 5s effective

    def test_explicit_crawl_delay_wins_over_floor(self):
        """If robots.txt requires more than self.crawl_delay, the larger value wins."""
        mgr = EthicalScrapingManager()
        mgr.configure(crawl_delay=1.0, robots_cache_ttl_minutes=15)
        mgr.last_request_time["slow.com"] = time.time() + 2.0
        sleep_times = []
        with patch("capcat.core.ethical_scraping.time.sleep", side_effect=lambda s: sleep_times.append(s)):
            mgr.enforce_rate_limit("slow.com", crawl_delay=3.0, min_delay=1.0)
        assert sleep_times
        assert sleep_times[0] >= 2.5  # effective = max(3.0, 1.0, 1.0) = 3.0; slot 2s in future
