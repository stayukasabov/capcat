#!/usr/bin/env python3
"""
TDD Test Suite for Retry-and-Skip Logic

This test suite enforces strict TDD discipline for implementing
retry-and-skip logic for sources that timeout or refuse connection.

Test Coverage:
1. Source skips after 2 failed connection attempts
2. Batch processing continues with remaining sources
3. Skipped sources appear in final summary
4. Successful retry on second attempt
5. Configurable max_retries parameter
6. Multiple URL fallbacks exhaustion
7. Skip reporting format and content
"""

import time
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import requests

from core.source_system.base_source import (
    Article,
    BaseSource,
    SourceConfig,
    ArticleDiscoveryError,
)


class MockSource(BaseSource):
    """Mock source implementation for testing."""

    def __init__(self, config, session=None, fail_count=0):
        super().__init__(config, session)
        self.fail_count = fail_count
        self.attempt_count = 0

    @property
    def source_type(self) -> str:
        return "custom"

    def discover_articles(self, count: int):
        """Mock discover that fails N times before succeeding."""
        self.attempt_count += 1
        if self.attempt_count <= self.fail_count:
            raise requests.exceptions.Timeout(
                f"Timeout on attempt {self.attempt_count}"
            )
        return [
            Article(title=f"Article {i}", url=f"http://test.com/{i}")
            for i in range(count)
        ]

    def fetch_article_content(self, article, output_dir, progress_callback=None):
        return True, "article_path"


class TestRetrySkipLogic(unittest.TestCase):
    """Test retry-and-skip logic for network resilience."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = SourceConfig(
            name="test_source",
            display_name="Test Source",
            base_url="https://test.com",
            timeout=10.0,
            rate_limit=1.0,
        )

    def test_source_skips_after_two_timeouts(self):
        """
        RED PHASE TEST #1

        Source should skip after 2 failed connection attempts.
        Expected behavior:
        - Attempt 1: Timeout -> log warning
        - Attempt 2: Timeout -> log warning
        - Decision: Skip source -> log skip -> return None
        """
        source = MockSource(self.config, fail_count=3)

        # This should fail because retry-skip logic doesn't exist yet
        with patch('core.source_system.base_source.get_logger') as mock_logger:
            logger = MagicMock()
            mock_logger.return_value = logger

            # Expect None return after 2 failures (skip)
            result = source.discover_articles_with_retry_skip(
                count=10,
                max_retries=2
            )

            # Verify skip behavior
            self.assertIsNone(result, "Source should return None after skip")

            # Verify logging
            self.assertEqual(
                logger.warning.call_count,
                2,
                "Should log warning for each failed attempt"
            )

            # Verify skip decision logged
            skip_calls = [
                call for call in logger.warning.call_args_list
                if 'skip' in str(call).lower()
            ]
            self.assertGreater(
                len(skip_calls),
                0,
                "Should log skip decision"
            )

    def test_successful_retry_on_second_attempt(self):
        """
        RED PHASE TEST #2

        Source succeeds if retry works on second attempt.
        Expected behavior:
        - Attempt 1: Timeout -> log warning -> retry
        - Attempt 2: Success -> return articles
        """
        source = MockSource(self.config, fail_count=1)

        with patch('core.source_system.base_source.get_logger') as mock_logger:
            logger = MagicMock()
            mock_logger.return_value = logger

            # Should succeed on attempt 2
            result = source.discover_articles_with_retry_skip(
                count=10,
                max_retries=2
            )

            # Verify success
            self.assertIsNotNone(result, "Should return articles on successful retry")
            self.assertEqual(len(result), 10, "Should return requested count")

            # Verify one warning was logged (first failure)
            self.assertEqual(
                logger.warning.call_count,
                1,
                "Should log warning for first failed attempt only"
            )

    def test_batch_continues_after_source_skip(self):
        """
        RED PHASE TEST #3

        Batch processing continues with remaining sources after skip.
        Expected behavior:
        - Source 1: Fails -> Skip -> Continue
        - Source 2: Succeeds -> Process
        - Source 3: Succeeds -> Process
        """
        from core.unified_source_processor import UnifiedSourceProcessor

        processor = UnifiedSourceProcessor()

        # Mock sources: first fails, others succeed
        sources = {
            'source1': MockSource(
                SourceConfig(
                    name='source1',
                    display_name='Source 1',
                    base_url='http://test1.com'
                ),
                fail_count=3
            ),
            'source2': MockSource(
                SourceConfig(
                    name='source2',
                    display_name='Source 2',
                    base_url='http://test2.com'
                ),
                fail_count=0
            ),
            'source3': MockSource(
                SourceConfig(
                    name='source3',
                    display_name='Source 3',
                    base_url='http://test3.com'
                ),
                fail_count=0
            ),
        }

        results = []
        for source_name, source in sources.items():
            # This should fail because batch skip continuation doesn't exist
            result = processor.process_source_with_skip(
                source=source,
                count=10,
                max_retries=2
            )
            results.append((source_name, result))

        # Verify source1 was skipped
        self.assertIsNone(results[0][1], "First source should be skipped")

        # Verify source2 and source3 succeeded
        self.assertIsNotNone(results[1][1], "Second source should succeed")
        self.assertIsNotNone(results[2][1], "Third source should succeed")

    def test_skip_reported_in_summary(self):
        """
        RED PHASE TEST #4

        Skipped sources appear in final summary.
        Expected behavior:
        - Track skipped sources
        - Include in summary with reason
        - Format: "Skipped: source_name (reason: 2 timeouts)"
        """
        from core.unified_source_processor import UnifiedSourceProcessor

        processor = UnifiedSourceProcessor()

        source = MockSource(self.config, fail_count=3)

        # This should fail because skip tracking doesn't exist
        summary = processor.process_batch_with_summary(
            sources={'test_source': source},
            count=10,
            max_retries=2
        )

        # Verify summary contains skip information
        self.assertIn('skipped', summary, "Summary should contain skip section")
        self.assertIn(
            'test_source',
            summary['skipped'],
            "Skipped source should be in summary"
        )
        self.assertIn(
            'timeout',
            summary['skipped']['test_source']['reason'].lower(),
            "Skip reason should mention timeout"
        )
        self.assertEqual(
            summary['skipped']['test_source']['attempts'],
            2,
            "Should track number of attempts"
        )

    def test_configurable_max_retries(self):
        """
        RED PHASE TEST #5

        Max retries should be configurable.
        Expected behavior:
        - max_retries=1: Skip after 1 failure
        - max_retries=3: Skip after 3 failures
        - max_retries=5: Skip after 5 failures
        """
        test_cases = [
            (1, 2),  # max_retries=1, fail_count=2 -> should skip
            (3, 4),  # max_retries=3, fail_count=4 -> should skip
            (5, 6),  # max_retries=5, fail_count=6 -> should skip
        ]

        for max_retries, fail_count in test_cases:
            with self.subTest(max_retries=max_retries, fail_count=fail_count):
                source = MockSource(self.config, fail_count=fail_count)

                # This should fail because configurable retries don't exist
                result = source.discover_articles_with_retry_skip(
                    count=10,
                    max_retries=max_retries
                )

                # Verify skip occurred
                self.assertIsNone(
                    result,
                    f"Should skip after {max_retries} failures"
                )

                # Verify attempt count
                self.assertEqual(
                    source.attempt_count,
                    max_retries,
                    f"Should attempt exactly {max_retries} times"
                )

    def test_multiple_url_fallbacks_exhaustion(self):
        """
        RED PHASE TEST #6

        Source should try all URL fallbacks before skipping.
        Expected behavior:
        - Try URL 1 -> Timeout
        - Try URL 2 -> Timeout
        - Try URL 3 -> Timeout
        - Skip after all URLs exhausted
        """
        urls = [
            'https://test.com/newest.rss',
            'https://test.com/rss',
            'https://test.com/newest',
        ]

        source = MockSource(self.config, fail_count=6)  # Fail all attempts

        with patch('core.source_system.base_source.get_logger') as mock_logger:
            logger = MagicMock()
            mock_logger.return_value = logger

            # This should fail because URL fallback logic doesn't exist
            result = source.discover_articles_with_url_fallbacks(
                count=10,
                urls=urls,
                max_retries_per_url=2
            )

            # Verify skip after all URLs exhausted
            self.assertIsNone(result, "Should skip after all URLs exhausted")

            # Verify all URLs were tried
            warning_calls = logger.warning.call_args_list
            for url in urls:
                url_mentioned = any(
                    url in str(call) for call in warning_calls
                )
                self.assertTrue(
                    url_mentioned,
                    f"Should have tried URL: {url}"
                )

    def test_skip_logging_format(self):
        """
        RED PHASE TEST #7

        Skip logging should follow specific format.
        Expected format:
        - WARNING: Timeout accessing https://lobste.rs/newest.rss (attempt 1/2)
        - WARNING: Timeout accessing https://lobste.rs/rss (attempt 2/2)
        - WARNING: Skipping source 'lobsters' after 2 failed attempts
        """
        source = MockSource(self.config, fail_count=3)

        with patch('core.source_system.base_source.get_logger') as mock_logger:
            logger = MagicMock()
            mock_logger.return_value = logger

            # This should fail because formatted logging doesn't exist
            result = source.discover_articles_with_retry_skip(
                count=10,
                max_retries=2
            )

            # Verify logging format
            warning_calls = [str(call) for call in logger.warning.call_args_list]

            # Check attempt logging
            attempt_logs = [
                log for log in warning_calls if 'attempt' in log.lower()
            ]
            self.assertGreater(
                len(attempt_logs),
                0,
                "Should log attempts with 'attempt X/Y' format"
            )

            # Check skip decision logging
            skip_logs = [
                log for log in warning_calls
                if 'skip' in log.lower() and 'after' in log.lower()
            ]
            self.assertEqual(
                len(skip_logs),
                1,
                "Should log exactly one skip decision"
            )

    def test_connection_error_also_triggers_skip(self):
        """
        RED PHASE TEST #8

        Connection errors (not just timeouts) should trigger skip logic.
        Expected behavior:
        - Attempt 1: ConnectionError -> log warning
        - Attempt 2: ConnectionError -> log warning
        - Decision: Skip source -> log skip
        """
        class ConnectionErrorSource(MockSource):
            def discover_articles(self, count: int):
                self.attempt_count += 1
                if self.attempt_count <= self.fail_count:
                    raise requests.exceptions.ConnectionError(
                        f"Connection refused on attempt {self.attempt_count}"
                    )
                return [Article(title="Test", url="http://test.com")]

        source = ConnectionErrorSource(self.config, fail_count=3)

        with patch('core.source_system.base_source.get_logger') as mock_logger:
            logger = MagicMock()
            mock_logger.return_value = logger

            # This should fail because ConnectionError skip doesn't exist
            result = source.discover_articles_with_retry_skip(
                count=10,
                max_retries=2
            )

            # Verify skip occurred
            self.assertIsNone(result, "Should skip after ConnectionError failures")

            # Verify appropriate errors were logged
            error_logs = [str(call) for call in logger.warning.call_args_list]
            connection_errors = [
                log for log in error_logs if 'connection' in log.lower()
            ]
            self.assertGreater(
                len(connection_errors),
                0,
                "Should log connection errors"
            )


class TestRetrySkipIntegration(unittest.TestCase):
    """Integration tests for retry-skip logic in real scenarios."""

    def test_lobsters_source_skip_integration(self):
        """
        RED PHASE INTEGRATION TEST

        Test real lobsters source with retry-skip logic.
        Simulates actual timeout scenario.
        """
        from sources.active.custom.lb.source import LbSource

        config = SourceConfig(
            name='lb',
            display_name='Lobsters',
            base_url='https://lobste.rs',
            timeout=5.0,
        )

        # Mock session to simulate timeouts
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.Timeout(
            "Connection timeout"
        )

        source = LbSource(config, session=mock_session)

        # This should fail because LbSource doesn't implement retry-skip yet
        with patch('sources.active.custom.lb.source.get_logger') as mock_logger:
            logger = MagicMock()
            mock_logger.return_value = logger

            try:
                result = source.discover_articles(count=10)
                # Should return None (skip) instead of raising exception
                self.assertIsNone(result, "Should skip after timeout failures")
            except ArticleDiscoveryError:
                self.fail("Should skip instead of raising ArticleDiscoveryError")


if __name__ == '__main__':
    unittest.main()
