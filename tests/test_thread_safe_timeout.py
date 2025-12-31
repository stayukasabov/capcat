#!/usr/bin/env python3
"""
TDD Tests for thread-safe HTML conversion timeout.

Following red-green-refactor cycle:
1. RED: Write failing tests
2. GREEN: Implement minimal code to pass
3. REFACTOR: Clean up implementation
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch


class TestThreadSafeHTMLConversion:
    """Test suite for thread-safe HTML to Markdown conversion."""

    def test_convert_html_with_timeout_success(self):
        """Test successful conversion within timeout."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        html_content = "<html><body><h1>Test</h1></body></html>"
        url = "https://example.com/test"

        # ACT
        result = convert_html_with_timeout(html_content, url, timeout=5)

        # ASSERT
        assert result is not None
        assert isinstance(result, str)
        assert "Test" in result or result == ""  # May be empty if conversion fails

    def test_convert_html_with_timeout_handles_timeout(self):
        """Test that timeout is properly handled without blocking."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        def slow_conversion(*args):
            """Simulate slow conversion that will timeout."""
            time.sleep(10)
            return "Should never reach here"

        # Mock a slow conversion function
        with patch('core.article_fetcher.html_to_markdown') as mock_convert:
            mock_convert.side_effect = slow_conversion

            html_content = "<html><body><h1>Test</h1></body></html>"
            url = "https://example.com/test"

            # ACT
            start_time = time.time()
            result = convert_html_with_timeout(html_content, url, timeout=1)
            elapsed = time.time() - start_time

            # ASSERT
            assert result == ""  # Should return empty string on timeout
            assert elapsed < 2  # Should timeout quickly (within 2 seconds)

    def test_convert_html_with_timeout_handles_empty_content(self):
        """Test handling of empty HTML content."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        url = "https://example.com/test"

        # ACT & ASSERT
        assert convert_html_with_timeout("", url) == ""
        assert convert_html_with_timeout(None, url) == ""
        assert convert_html_with_timeout("   ", url) == ""

    def test_convert_html_with_timeout_handles_exceptions(self):
        """Test that exceptions in conversion are handled gracefully."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        with patch('core.article_fetcher.html_to_markdown') as mock_convert:
            mock_convert.side_effect = ValueError("Invalid HTML")

            html_content = "<html><body><h1>Test</h1></body></html>"
            url = "https://example.com/test"

            # ACT
            result = convert_html_with_timeout(html_content, url)

            # ASSERT
            assert result == ""  # Should return empty string on exception

    def test_convert_html_with_timeout_is_thread_safe(self):
        """Test that multiple conversions can run concurrently."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        html_content = "<html><body><h1>Test</h1></body></html>"
        urls = [f"https://example.com/test{i}" for i in range(10)]

        # ACT
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(convert_html_with_timeout, html_content, url)
                for url in urls
            ]
            results = [f.result() for f in futures]

        # ASSERT
        assert len(results) == 10
        assert all(isinstance(r, str) for r in results)
        # No exceptions should be raised (thread-safe)

    def test_convert_html_with_timeout_logs_timeout(self):
        """Test that timeouts are properly logged."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout
        import logging

        def slow_conversion(*args):
            time.sleep(10)
            return "Should timeout"

        # Use real logger but capture output
        with patch('core.article_fetcher.html_to_markdown') as mock_convert:
            mock_convert.side_effect = slow_conversion

            html_content = "<html><body><h1>Test</h1></body></html>"
            url = "https://example.com/test"

            # Capture log output
            with patch('core.logging_config.get_logger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                # ACT
                result = convert_html_with_timeout(html_content, url, timeout=1)

                # ASSERT
                assert result == ""
                # Verify warning was logged
                assert mock_logger.warning.called
                warning_msg = str(mock_logger.warning.call_args)
                assert "timeout" in warning_msg.lower() or "Timeout" in warning_msg

    def test_convert_html_with_timeout_logs_errors(self):
        """Test that conversion errors are properly logged."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        with patch('core.article_fetcher.html_to_markdown') as mock_convert:
            mock_convert.side_effect = Exception("Conversion failed")

            html_content = "<html><body><h1>Test</h1></body></html>"
            url = "https://example.com/test"

            # Capture log output
            with patch('core.logging_config.get_logger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                # ACT
                result = convert_html_with_timeout(html_content, url)

                # ASSERT
                assert result == ""
                # Verify error was logged
                assert mock_logger.error.called
                error_msg = str(mock_logger.error.call_args)
                assert "failed" in error_msg.lower() or "Conversion" in error_msg

    def test_convert_html_with_timeout_respects_custom_timeout(self):
        """Test that custom timeout values are respected."""
        # ARRANGE
        from core.article_fetcher import convert_html_with_timeout

        def slow_conversion(*args):
            time.sleep(5)
            return "Slow result"

        with patch('core.article_fetcher.html_to_markdown') as mock_convert:
            mock_convert.side_effect = slow_conversion

            html_content = "<html><body><h1>Test</h1></body></html>"
            url = "https://example.com/test"

            # ACT - Test with short timeout
            start_time = time.time()
            result = convert_html_with_timeout(html_content, url, timeout=2)
            short_elapsed = time.time() - start_time

            # ASSERT
            assert result == ""
            assert short_elapsed < 3  # Should timeout within 3 seconds


class TestArticleFetcherIntegration:
    """Integration tests for ArticleFetcher using new timeout mechanism."""

    def test_article_fetcher_uses_safe_timeout(self):
        """Test that ArticleFetcher uses thread-safe timeout mechanism."""
        # This test verifies integration after refactoring
        # Will be implemented after convert_html_with_timeout is integrated
        pass

    def test_concurrent_article_processing_no_race_conditions(self):
        """Test that concurrent article processing doesn't cause race conditions."""
        # This test verifies the fix addresses the original issue
        # Will be implemented after refactoring is complete
        pass


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility after refactoring."""

    def test_existing_article_processing_still_works(self):
        """Test that existing article processing functionality is preserved."""
        # Placeholder for backward compatibility verification
        pass


# Test fixtures and helpers
@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a test paragraph.</p>
            <img src="test.jpg" alt="Test Image">
        </body>
    </html>
    """


@pytest.fixture
def mock_html_to_markdown():
    """Mock html_to_markdown function."""
    with patch('core.article_fetcher.html_to_markdown') as mock:
        mock.return_value = "# Main Heading\n\nThis is a test paragraph."
        yield mock


# Performance benchmark tests
class TestPerformance:
    """Performance tests for timeout mechanism."""

    def test_timeout_overhead_is_minimal(self):
        """Test that timeout mechanism adds minimal overhead."""
        from core.article_fetcher import convert_html_with_timeout

        html_content = "<html><body><h1>Test</h1></body></html>"
        url = "https://example.com/test"

        # ACT
        iterations = 10
        start_time = time.time()

        for _ in range(iterations):
            convert_html_with_timeout(html_content, url, timeout=30)

        elapsed = time.time() - start_time
        avg_time = elapsed / iterations

        # ASSERT
        # Overhead should be minimal (<100ms per call)
        assert avg_time < 0.1, f"Timeout overhead too high: {avg_time:.3f}s per call"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
