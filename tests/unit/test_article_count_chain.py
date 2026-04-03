"""Tests for article_count None propagation through SourceConfig and _resolve_count."""
import pytest
from capcat.core.source_system.base_source import SourceConfig


def _cfg(**kwargs) -> SourceConfig:
    defaults = dict(name="test", display_name="Test", base_url="https://test.com")
    defaults.update(kwargs)
    return SourceConfig(**defaults)


class TestSourceConfigArticleCount:
    def test_default_is_none(self):
        cfg = _cfg()
        assert cfg.article_count is None

    def test_explicit_count_preserved(self):
        cfg = _cfg(article_count=50)
        assert cfg.article_count == 50

    def test_zero_raises_value_error(self):
        with pytest.raises(ValueError):
            _cfg(article_count=0)

    def test_none_does_not_raise(self):
        """None must not trigger the guard that rejects <= 0."""
        cfg = _cfg(article_count=None)
        assert cfg.article_count is None


class TestResolveCount:
    def _resolve(self, cli_count, source_count, global_count):
        from capcat.core.unified_source_processor import _resolve_count
        from unittest.mock import MagicMock

        source_config = MagicMock()
        source_config.article_count = source_count

        config = MagicMock()
        config.processing.article_count = global_count

        return _resolve_count(cli_count, source_config, config)

    def test_cli_count_wins(self):
        assert self._resolve(cli_count=5, source_count=10, global_count=30) == 5

    def test_source_count_wins_over_global(self):
        assert self._resolve(cli_count=None, source_count=10, global_count=30) == 10

    def test_global_count_used_when_source_is_none(self):
        assert self._resolve(cli_count=None, source_count=None, global_count=30) == 30

    def test_global_count_used_when_all_none(self):
        assert self._resolve(cli_count=None, source_count=None, global_count=42) == 42
