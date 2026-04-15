"""
Regression tests — BUG F3: network.max_retries config is dead code.
network_retry was hardcoding max_retries=3 instead of reading from config.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestNetworkRetryRespectsConfig:
    """network_retry must honour config.network.max_retries."""

    def _make_failing_func(self):
        """Return a function that always raises ConnectionError, and a call counter."""
        call_count = {"n": 0}

        def always_fails():
            call_count["n"] += 1
            raise ConnectionError("simulated failure")

        return always_fails, call_count

    def _mock_config(self, max_retries: int):
        cfg = MagicMock()
        cfg.network.max_retries = max_retries
        cfg.network.retry_delay = 0.0  # no sleep in tests
        return cfg

    def test_zero_retries_attempts_once(self):
        """When max_retries=0, network_retry must call the function exactly once."""
        from capcat.core.retry import network_retry

        func, counter = self._make_failing_func()
        decorated = network_retry(func)

        with patch("capcat.core.retry.get_config", return_value=self._mock_config(0)):
            with pytest.raises(ConnectionError):
                decorated()

        assert counter["n"] == 1, (
            f"Expected 1 attempt, got {counter['n']}. "
            "network_retry is not reading max_retries from config."
        )

    def test_one_retry_attempts_twice(self):
        """When max_retries=1, network_retry must call the function exactly twice."""
        from capcat.core.retry import network_retry

        func, counter = self._make_failing_func()
        decorated = network_retry(func)

        with patch("capcat.core.retry.get_config", return_value=self._mock_config(1)):
            with pytest.raises(ConnectionError):
                decorated()

        assert counter["n"] == 2, (
            f"Expected 2 attempts, got {counter['n']}."
        )

    def test_config_default_three_gives_four_attempts(self):
        """Default config max_retries=3 means 4 total attempts (1 + 3 retries)."""
        from capcat.core.retry import network_retry

        func, counter = self._make_failing_func()
        decorated = network_retry(func)

        with patch("capcat.core.retry.get_config", return_value=self._mock_config(3)):
            with pytest.raises(ConnectionError):
                decorated()

        assert counter["n"] == 4, (
            f"Expected 4 attempts (1 + 3 retries), got {counter['n']}."
        )
