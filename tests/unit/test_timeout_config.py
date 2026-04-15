"""
Regression tests — BUG F2: network.connect_timeout config is dead code.
get_timeout_for_source was returning SOURCE_TIMEOUTS["default"] instead of
reading config.network.connect_timeout / read_timeout for unknown sources.
"""
from unittest.mock import MagicMock, patch


def _mock_network_config(connect_timeout: int, read_timeout: int):
    cfg = MagicMock()
    cfg.network.connect_timeout = connect_timeout
    cfg.network.read_timeout = read_timeout
    return cfg


class TestGetTimeoutForSourceUsesConfig:
    """get_timeout_for_source must fall back to config values for unknown sources."""

    def test_unknown_source_uses_config_connect_timeout(self):
        """Unknown source must use config.network.connect_timeout, not hardcoded 10."""
        from capcat.core.timeout_config import get_timeout_for_source

        with patch(
            "capcat.core.timeout_config.get_config",
            return_value=_mock_network_config(2, 30),
        ):
            tc = get_timeout_for_source("completely_unknown_source_xyz", use_adaptive=False)

        assert tc.connect_timeout == 2, (
            f"Expected connect_timeout=2 from config, got {tc.connect_timeout}. "
            "get_timeout_for_source is not reading config.network.connect_timeout."
        )

    def test_unknown_source_uses_config_read_timeout(self):
        """Unknown source must use config.network.read_timeout, not hardcoded 30."""
        from capcat.core.timeout_config import get_timeout_for_source

        with patch(
            "capcat.core.timeout_config.get_config",
            return_value=_mock_network_config(10, 5),
        ):
            tc = get_timeout_for_source("completely_unknown_source_xyz", use_adaptive=False)

        assert tc.read_timeout == 5, (
            f"Expected read_timeout=5 from config, got {tc.read_timeout}. "
            "get_timeout_for_source is not reading config.network.read_timeout."
        )

    def test_known_source_ignores_config(self):
        """Known source-specific overrides must still take precedence over config."""
        from capcat.core.timeout_config import get_timeout_for_source, SOURCE_TIMEOUTS

        with patch(
            "capcat.core.timeout_config.get_config",
            return_value=_mock_network_config(1, 1),
        ):
            tc = get_timeout_for_source("guardian", use_adaptive=False)

        # guardian has source-specific override — must not be overridden by config
        assert tc.connect_timeout == SOURCE_TIMEOUTS["guardian"].connect_timeout
        assert tc.read_timeout == SOURCE_TIMEOUTS["guardian"].read_timeout
