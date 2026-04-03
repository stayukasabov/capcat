"""
Regression test for B3: "Capcat Info: Connecting to X..." must not be printed
in quiet mode. The message uses print() which bypasses the logging system.
After the fix, it must use self.logger.info() so -q suppresses it.
"""
import logging
import logging.handlers
from unittest.mock import MagicMock, patch


class TestConnectingMessageRespectsQuietMode:
    """'Connecting to X...' must not print in quiet mode."""

    def test_connecting_message_uses_logger_not_print(self, capsys):
        """
        discover_articles_with_retry_skip must NOT call print() for the
        'Connecting to X' status message. It must use self.logger.info().

        Current broken behaviour: print(f"Capcat Info: Connecting to {name}...")
        fires unconditionally — bypasses the logging system, appears in -q mode.

        Fixed behaviour: self.logger.info(f"Connecting to {name}...") — suppressed
        when console handler is at WARNING level (quiet mode).
        """
        from capcat.core.source_system.base_source import BaseSource, SourceConfig

        config = SourceConfig(
            name="test",
            display_name="Test Source",
            base_url="https://example.com",
        )

        class FakeSource(BaseSource):
            source_type = "fake"

            def discover_articles(self, count=10):
                return []

            def fetch_article(self, article):
                return None

            def fetch_article_content(self, url):
                return None

        source = FakeSource(config=config)

        source.discover_articles_with_retry_skip(count=1, max_retries=2)

        captured = capsys.readouterr()
        assert "Connecting to" not in captured.out, (
            "'Connecting to' message must not go to stdout via print(). "
            "Use self.logger.info() so it respects quiet mode."
        )

    def test_connecting_message_is_logged_at_info(self):
        """
        The 'Connecting to X' message must be emitted at INFO level through
        the logger so it appears in normal mode but not in quiet mode.
        """
        from capcat.core.source_system.base_source import BaseSource, SourceConfig

        config = SourceConfig(
            name="test",
            display_name="Test Source",
            base_url="https://example.com",
        )

        class FakeSource(BaseSource):
            source_type = "fake"

            def discover_articles(self, count=10):
                return []

            def fetch_article(self, article):
                return None

            def fetch_article_content(self, url):
                return None

        source = FakeSource(config=config)

        log_records = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                log_records.append(record)

        capturing = CapturingHandler()
        capturing.setLevel(logging.DEBUG)
        source.logger.addHandler(capturing)
        source.logger.setLevel(logging.DEBUG)

        source.discover_articles_with_retry_skip(count=1, max_retries=2)

        source.logger.removeHandler(capturing)

        info_msgs = [r.getMessage() for r in log_records if r.levelno == logging.INFO]
        assert any("Connecting to" in m or "Test Source" in m for m in info_msgs), (
            f"Expected an INFO log containing 'Connecting to' or 'Test Source'. "
            f"Got INFO messages: {info_msgs}"
        )
