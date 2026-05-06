"""
Regression tests - BUG F3: network.max_retries config is dead code.
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


class TestNetworkRetryDoesNotRetry4xx:
    """network_retry must not retry HTTP 4xx errors (client errors are permanent)."""

    def _mock_config(self, max_retries: int = 3):
        cfg = MagicMock()
        cfg.network.max_retries = max_retries
        cfg.network.retry_delay = 0.0
        return cfg

    def test_http_403_not_retried(self):
        """HTTPError (403) must cause one attempt only, no retries."""
        import requests
        from capcat.core.retry import network_retry

        call_count = {"n": 0}

        def raises_403():
            call_count["n"] += 1
            response = MagicMock()
            response.status_code = 403
            raise requests.exceptions.HTTPError(response=response)

        decorated = network_retry(raises_403)

        with patch("capcat.core.retry.get_config", return_value=self._mock_config(3)):
            with pytest.raises(requests.exceptions.HTTPError):
                decorated()

        assert call_count["n"] == 1, (
            f"Expected 1 attempt (no retry on 403), got {call_count['n']}. "
            "network_retry is retrying HTTP 4xx errors."
        )

    def test_http_404_not_retried(self):
        """HTTPError (404) must cause one attempt only, no retries."""
        import requests
        from capcat.core.retry import network_retry

        call_count = {"n": 0}

        def raises_404():
            call_count["n"] += 1
            response = MagicMock()
            response.status_code = 404
            raise requests.exceptions.HTTPError(response=response)

        decorated = network_retry(raises_404)

        with patch("capcat.core.retry.get_config", return_value=self._mock_config(3)):
            with pytest.raises(requests.exceptions.HTTPError):
                decorated()

        assert call_count["n"] == 1, (
            f"Expected 1 attempt (no retry on 404), got {call_count['n']}."
        )

    def test_connection_error_still_retried(self):
        """ConnectionError must still be retried (it is transient)."""
        import requests
        from capcat.core.retry import network_retry

        call_count = {"n": 0}

        def raises_connection_error():
            call_count["n"] += 1
            raise requests.exceptions.ConnectionError("simulated")

        decorated = network_retry(raises_connection_error)

        with patch("capcat.core.retry.get_config", return_value=self._mock_config(1)):
            with pytest.raises(requests.exceptions.ConnectionError):
                decorated()

        assert call_count["n"] == 2, (
            f"Expected 2 attempts (1 + 1 retry), got {call_count['n']}."
        )
