"""
Regression test for: robots.txt Crawl-delay must NOT be used for rate limiting.

Root cause:
    HN's robots.txt sets Crawl-delay: 30.  enforce_rate_limit computed
    effective_delay = max(crawl_delay, min_delay, self.crawl_delay), so with
    crawl_delay=30, every back-to-back hit to news.ycombinator.com waited 30s.
    With 30 HN articles each fetching comments from the same domain, total wait
    = 29 × 30 = 870 seconds (14+ minutes).

Fix:
    enforce_rate_limit ignores the robots.txt crawl_delay parameter.
    effective_delay = max(min_delay, self.crawl_delay).
    robots.txt allow/disallow is still respected (via can_fetch / get_robots_txt).
"""
import time
from unittest.mock import patch

import pytest

from capcat.core.ethical_scraping import EthicalScrapingManager


class TestEnforceRateLimitIgnoresRobotsCrawlDelay:
    """robots.txt Crawl-delay: 30 must not serialise comment fetches at 30s intervals."""

    def _manager(self, crawl_delay: float = 0.1) -> EthicalScrapingManager:
        m = EthicalScrapingManager()
        m.configure(crawl_delay=crawl_delay, robots_cache_ttl_minutes=60)
        return m

    def test_high_robots_crawl_delay_not_applied(self):
        """Back-to-back requests with robots crawl_delay=30 must not sleep 30s."""
        manager = self._manager(crawl_delay=0.1)
        domain = "https://news.ycombinator.com"
        # Simulate a domain that was just fetched (elapsed ≈ 0)
        manager.last_request_time[domain] = time.time()

        sleep_calls = []

        def capture_sleep(t):
            sleep_calls.append(t)

        with patch("capcat.core.ethical_scraping.time.sleep", side_effect=capture_sleep):
            manager.enforce_rate_limit(domain, crawl_delay=30.0, min_delay=0.0)

        # Before fix: sleeps 30 seconds (robots.txt crawl_delay wins)
        # After fix: sleeps at most self.crawl_delay (0.1s) or 0 if enough time elapsed
        if sleep_calls:
            assert max(sleep_calls) < 1.0, (
                f"enforce_rate_limit would sleep {max(sleep_calls):.1f}s due to robots.txt "
                "Crawl-delay: 30. robots.txt crawl_delay must not override user config."
            )

    def test_config_crawl_delay_still_applied(self):
        """User's configured crawl_delay is still enforced (robots.txt crawl_delay is just ignored)."""
        manager = self._manager(crawl_delay=0.5)
        domain = "https://news.ycombinator.com"
        manager.last_request_time[domain] = time.time()

        sleep_calls = []

        def capture_sleep(t):
            sleep_calls.append(t)

        with patch("capcat.core.ethical_scraping.time.sleep", side_effect=capture_sleep):
            manager.enforce_rate_limit(domain, crawl_delay=30.0, min_delay=0.0)

        # The user's crawl_delay (0.5s) must still be applied, not 30s
        assert sleep_calls, "Expected a sleep based on user's crawl_delay=0.5s"
        assert max(sleep_calls) <= 0.6, (
            f"sleep was {max(sleep_calls):.2f}s - expected ≤ 0.6s (user crawl_delay=0.5s)"
        )
        assert max(sleep_calls) < 30.0, "robots.txt crawl_delay=30 must not be used"

    def test_min_delay_still_applied(self):
        """min_delay is still enforced even when robots crawl_delay is ignored."""
        manager = self._manager(crawl_delay=0.0)
        domain = "https://example.com"
        manager.last_request_time[domain] = time.time()

        sleep_calls = []

        def capture_sleep(t):
            sleep_calls.append(t)

        with patch("capcat.core.ethical_scraping.time.sleep", side_effect=capture_sleep):
            manager.enforce_rate_limit(domain, crawl_delay=30.0, min_delay=1.0)

        # min_delay=1.0 must be applied; robots.txt 30s ignored
        assert sleep_calls, "Expected a sleep based on min_delay=1.0"
        assert max(sleep_calls) <= 1.1, (
            f"sleep was {max(sleep_calls):.2f}s - expected ≤ 1.1s (min_delay=1.0)"
        )
        assert max(sleep_calls) < 30.0, "robots.txt crawl_delay=30 must not be used"
