#!/usr/bin/env python3
"""
Regression tests for EthicalScrapingManager.enforce_rate_limit thread safety.

Bug: enforce_rate_limit reads and writes last_request_time without a lock.
Two concurrent threads hitting the same domain both pass the elapsed check
and both fire at the same time - the per-domain delay is not enforced.
"""

import threading
import time

import pytest

import capcat.core.ethical_scraping as _esm
from capcat.core.ethical_scraping import EthicalScrapingManager


def _fresh_manager() -> EthicalScrapingManager:
    """Return a new EthicalScrapingManager with no prior state."""
    _esm._global_manager = None
    return EthicalScrapingManager()


@pytest.fixture(autouse=True)
def _reset_global_manager():
    """Restore _global_manager to its original value after each test."""
    original = _esm._global_manager
    yield
    _esm._global_manager = original


class TestEnforceRateLimitThreadSafety:
    """enforce_rate_limit must serialize concurrent requests to the same domain."""

    def test_two_concurrent_threads_are_spaced_by_min_delay(self):
        """
        Two threads calling enforce_rate_limit for the same domain concurrently
        must fire at least min_delay apart (consecutive spacing, not just first-to-last).
        """
        manager = _fresh_manager()
        domain = "https://news.ycombinator.com"
        min_delay = 0.15

        fire_times = []
        lock = threading.Lock()
        barrier = threading.Barrier(2)

        def worker():
            barrier.wait()
            manager.enforce_rate_limit(domain, crawl_delay=0.0, min_delay=min_delay)
            with lock:
                fire_times.append(time.monotonic())

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert len(fire_times) == 2, "Both threads must complete"
        fire_times.sort()
        gap = fire_times[1] - fire_times[0]
        assert gap >= min_delay * 0.85, (
            f"Threads fired only {gap:.3f}s apart - expected >= {min_delay * 0.85:.3f}s. "
            "enforce_rate_limit is not thread-safe."
        )

    def test_four_concurrent_threads_are_each_spaced_by_min_delay(self):
        """
        Four threads must each be spaced at least min_delay apart
        (first to last >= 3 * min_delay).
        """
        manager = _fresh_manager()
        domain = "https://news.ycombinator.com"
        min_delay = 0.05

        fire_times = []
        lock = threading.Lock()
        barrier = threading.Barrier(4)

        def worker():
            barrier.wait()
            manager.enforce_rate_limit(domain, crawl_delay=0.0, min_delay=min_delay)
            with lock:
                fire_times.append(time.monotonic())

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert len(fire_times) == 4, "All four threads must complete"
        fire_times.sort()
        total_spread = fire_times[-1] - fire_times[0]
        assert total_spread >= min_delay * 3 * 0.75, (
            f"Total spread {total_spread:.3f}s too small for 4 threads with {min_delay}s delay. "
            "enforce_rate_limit is not serializing concurrent access."
        )

    def test_different_domains_are_not_serialized(self):
        """
        Requests to different domains must NOT be delayed by each other.
        """
        manager = _fresh_manager()
        min_delay = 0.1
        barrier = threading.Barrier(2)
        fire_times = {}
        lock = threading.Lock()

        def worker(domain):
            barrier.wait()
            manager.enforce_rate_limit(domain, crawl_delay=0.0, min_delay=min_delay)
            with lock:
                fire_times[domain] = time.monotonic()

        domains = ["https://news.ycombinator.com", "https://lobste.rs"]
        threads = [threading.Thread(target=worker, args=(d,)) for d in domains]
        start = time.monotonic()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)
        elapsed = time.monotonic() - start

        assert len(fire_times) == 2, "Both threads must complete"
        assert elapsed < min_delay * 1.8, (
            f"Different domains took {elapsed:.3f}s - they are being serialized when they should not be."
        )
