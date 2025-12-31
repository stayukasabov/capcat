"""
Test suite for PDF download skip feature with ESC key prompt.

Tests the TDD implementation of:
- HEAD request size checking
- User prompt with countdown
- ESC key detection
- Integration with _fetch_web_content()
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.article_fetcher import ArticleFetcher
from core.config import get_config


class ConcreteArticleFetcher(ArticleFetcher):
    """Concrete implementation of ArticleFetcher for testing."""

    def should_skip_url(self, url: str, title: str) -> bool:
        """Test implementation always returns False."""
        return False


class TestPDFSkipPrompt(unittest.TestCase):
    """Test PDF size checking and skip prompt functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = get_config()
        mock_session = Mock()
        self.fetcher = ConcreteArticleFetcher(
            session=mock_session,
            download_files=False
        )
        # session already mocked in ConcreteArticleFetcher init above

    def test_check_pdf_size_small_file(self):
        """
        Test that small PDF files (< 5MB) proceed without prompt.

        Given: A PDF URL with Content-Length of 2MB
        When: _check_pdf_size_and_prompt() is called
        Then: Should return False (proceed) without showing prompt
        """
        url = "https://example.com/document.pdf"
        title = "Test Document"

        # Mock HEAD request returning 2MB file
        mock_response = Mock()
        mock_response.headers = {'Content-Length': str(2 * 1024 * 1024)}
        mock_response.status_code = 200

        with patch.object(
            self.fetcher.session,
            'head',
            return_value=mock_response
        ) as mock_head:
            result = self.fetcher._check_pdf_size_and_prompt(url, title)

            mock_head.assert_called_once_with(
                url,
                timeout=self.config.network.connect_timeout,
                allow_redirects=True
            )
            self.assertFalse(result, "Small PDF should proceed without prompt")

    def test_check_pdf_size_large_file_user_skips(self):
        """
        Test that large PDF files (> 5MB) show prompt and user can skip.

        Given: A PDF URL with Content-Length of 10MB
        When: User presses ESC during countdown
        Then: Should return True (skip download)
        """
        url = "https://example.com/large-document.pdf"
        title = "Large Test Document"

        # Mock HEAD request returning 10MB file
        mock_response = Mock()
        mock_response.headers = {'Content-Length': str(10 * 1024 * 1024)}
        mock_response.status_code = 200

        with patch.object(
            self.fetcher.session,
            'head',
            return_value=mock_response
        ):
            # Mock _prompt_user_skip to simulate ESC key press
            with patch.object(
                self.fetcher,
                '_prompt_user_skip',
                return_value=True
            ) as mock_prompt:
                result = self.fetcher._check_pdf_size_and_prompt(url, title)

                mock_prompt.assert_called_once()
                # Check that size_mb argument is approximately 10
                call_args = mock_prompt.call_args
                self.assertEqual(call_args[0][0], title)
                self.assertAlmostEqual(call_args[0][1], 10.0, places=1)

                self.assertTrue(result, "ESC press should skip download")

    def test_check_pdf_size_large_file_timeout(self):
        """
        Test that large PDF files proceed on timeout (no ESC press).

        Given: A PDF URL with Content-Length of 10MB
        When: No ESC key press within 20 seconds
        Then: Should return False (proceed with download)
        """
        url = "https://example.com/large-document.pdf"
        title = "Large Test Document"

        # Mock HEAD request returning 10MB file
        mock_response = Mock()
        mock_response.headers = {'Content-Length': str(10 * 1024 * 1024)}
        mock_response.status_code = 200

        with patch.object(
            self.fetcher.session,
            'head',
            return_value=mock_response
        ):
            # Mock _prompt_user_skip to simulate timeout (no ESC)
            with patch.object(
                self.fetcher,
                '_prompt_user_skip',
                return_value=False
            ) as mock_prompt:
                result = self.fetcher._check_pdf_size_and_prompt(url, title)

                mock_prompt.assert_called_once()
                self.assertFalse(result, "Timeout should proceed with download")

    def test_check_pdf_size_head_request_fails(self):
        """
        Test that HEAD request failures proceed with download.

        Given: A PDF URL where HEAD request raises exception
        When: _check_pdf_size_and_prompt() is called
        Then: Should return False (proceed) and log warning
        """
        url = "https://example.com/document.pdf"
        title = "Test Document"

        # Mock HEAD request raising exception
        with patch.object(
            self.fetcher.session,
            'head',
            side_effect=Exception("Connection error")
        ):
            result = self.fetcher._check_pdf_size_and_prompt(url, title)

            self.assertFalse(result, "Failed HEAD should proceed with download")
            # Logger warning is called (verified by captured log output)

    def test_check_pdf_size_no_content_length_header(self):
        """
        Test that missing Content-Length header proceeds with download.

        Given: A PDF URL where HEAD response has no Content-Length
        When: _check_pdf_size_and_prompt() is called
        Then: Should return False (proceed)
        """
        url = "https://example.com/document.pdf"
        title = "Test Document"

        # Mock HEAD request with no Content-Length header
        mock_response = Mock()
        mock_response.headers = {}
        mock_response.status_code = 200

        with patch.object(
            self.fetcher.session,
            'head',
            return_value=mock_response
        ):
            result = self.fetcher._check_pdf_size_and_prompt(url, title)

            self.assertFalse(result, "Missing Content-Length should proceed")

    def test_prompt_user_skip_esc_pressed(self):
        """
        Test ESC key detection during countdown prompt.

        Given: A large PDF requiring user confirmation
        When: User presses ESC key within timeout period
        Then: Should return True immediately
        """
        title = "Large Document"
        size_mb = 15.5

        # Mock the threading.Event to simulate ESC press
        mock_event = Mock()
        mock_event.is_set.side_effect = [False, True]  # Not set, then set

        with patch('core.article_fetcher.threading.Event', return_value=mock_event):
            with patch('core.article_fetcher.keyboard.Listener') as mock_listener:
                mock_listener.return_value = Mock()
                # Mock time.sleep to speed up test
                with patch('core.article_fetcher.time.sleep'):
                    result = self.fetcher._prompt_user_skip(title, size_mb)

                    self.assertTrue(result, "ESC key should trigger skip")

    def test_prompt_user_skip_timeout(self):
        """
        Test timeout without ESC key press.

        Given: A large PDF requiring user confirmation
        When: Timeout period expires without ESC press
        Then: Should return False
        """
        title = "Large Document"
        size_mb = 15.5

        # Mock pynput keyboard listener without triggering ESC
        with patch('core.article_fetcher.keyboard') as mock_keyboard:
            mock_listener = Mock()
            mock_keyboard.Listener.return_value = mock_listener

            # Mock time.sleep to speed up test
            with patch('core.article_fetcher.time.sleep'):
                # Mock time.time to simulate timeout
                with patch('core.article_fetcher.time.time') as mock_time:
                    mock_time.side_effect = [0, 21]  # Start at 0, end at 21s

                    result = self.fetcher._prompt_user_skip(title, size_mb)

                    self.assertFalse(result, "Timeout should proceed with download")

    def test_fetch_web_content_skips_pdf_on_esc(self):
        """
        Test integration: _fetch_web_content skips PDF when user presses ESC.

        Given: A direct PDF URL passed to _fetch_web_content
        When: User presses ESC during prompt
        Then: Should return (True, None, None) - success but no content (user skip choice)
        """
        url = "https://example.com/document.pdf"
        title = "Test Document"
        index = 1
        base_folder = "/tmp/test"

        with patch.object(
            self.fetcher,
            '_check_pdf_size_and_prompt',
            return_value=True  # User chose to skip
        ) as mock_check:
            result = self.fetcher._fetch_web_content(
                title=title,
                url=url,
                index=index,
                base_folder=base_folder,
                progress_callback=None
            )

            # Verify check was called with is_direct_pdf=True for .pdf URLs
            mock_check.assert_called_once_with(url, title, is_direct_pdf=True)

            # Direct PDF skip should return success (user choice) but no content
            success, returned_title, content_path = result
            self.assertTrue(success, "Direct PDF skip should return success (user choice)")
            self.assertIsNone(returned_title)
            self.assertIsNone(content_path)

    def test_fetch_web_content_downloads_pdf_on_timeout(self):
        """
        Test integration: _fetch_web_content proceeds with PDF on timeout.

        Given: A PDF URL passed to _fetch_web_content
        When: User does not press ESC (timeout)
        Then: Should proceed to normal _fetch_url_with_retry flow
        """
        url = "https://example.com/document.pdf"
        title = "Test Document"
        index = 1
        base_folder = "/tmp/test"

        with patch.object(
            self.fetcher,
            '_check_pdf_size_and_prompt',
            return_value=False  # User chose to proceed
        ):
            with patch.object(
                self.fetcher,
                '_fetch_url_with_retry',
                side_effect=Exception("Test exception to stop flow")
            ) as mock_fetch:
                # The method should attempt to fetch
                try:
                    self.fetcher._fetch_web_content(
                        title=title,
                        url=url,
                        index=index,
                        base_folder=base_folder,
                        progress_callback=None
                    )
                except Exception:
                    pass  # Expected to fail when trying to fetch

                # Verify that _fetch_url_with_retry was called
                mock_fetch.assert_called()

    def test_fetch_web_content_non_pdf_bypasses_check(self):
        """
        Test that non-PDF URLs bypass the size check.

        Given: A non-PDF URL (e.g., .html)
        When: _fetch_web_content is called
        Then: Should not call _check_pdf_size_and_prompt
        """
        url = "https://example.com/article.html"
        title = "Test Article"
        index = 1
        base_folder = "/tmp/test"

        with patch.object(
            self.fetcher,
            '_check_pdf_size_and_prompt'
        ) as mock_check:
            with patch.object(
                self.fetcher,
                '_fetch_url_with_retry',
                side_effect=Exception("Test exception to stop flow")
            ):
                # The method should attempt to fetch without checking PDF
                try:
                    self.fetcher._fetch_web_content(
                        title=title,
                        url=url,
                        index=index,
                        base_folder=base_folder,
                        progress_callback=None
                    )
                except Exception:
                    pass  # Expected to fail

                # Verify PDF check was NOT called for non-PDF
                mock_check.assert_not_called()


    def test_create_skipped_pdf_placeholder(self):
        """
        Test that placeholder content is created for skipped PDFs.

        Given: A skipped PDF article
        When: _create_skipped_pdf_placeholder is called
        Then: Should create a text file with skip message and return success
        """
        import tempfile
        import shutil

        title = "Large Research Paper"
        url = "https://example.com/paper.pdf"
        index = 1

        # Create temporary directory for test
        base_folder = tempfile.mkdtemp()

        try:
            result = self.fetcher._create_skipped_pdf_placeholder(
                title=title,
                url=url,
                index=index,
                base_folder=base_folder
            )

            success, returned_title, content_path = result

            self.assertTrue(success, "Placeholder creation should succeed")
            self.assertEqual(returned_title, title)
            self.assertIsNotNone(content_path)
            self.assertTrue(
                os.path.exists(content_path),
                "Placeholder file should exist"
            )

            # Verify content contains skip message
            with open(content_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("PDF", content.upper())
                self.assertIn("SKIP", content.upper())
                self.assertIn(url, content)

        finally:
            # Cleanup
            shutil.rmtree(base_folder, ignore_errors=True)


    def test_no_stderr_warning_during_listener_creation(self):
        """
        Test that pynput accessibility warning is suppressed.

        Given: A large PDF requiring user confirmation
        When: Keyboard listener is created
        Then: No stderr output should appear (warning suppressed)
        """
        import io
        import sys

        title = "Test Document"
        size_mb = 10.0

        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()

        try:
            # Mock pynput to avoid actual keyboard listening
            with patch('core.article_fetcher.keyboard.Listener') as mock_listener:
                mock_listener.return_value = Mock()

                # Mock time to speed up test
                with patch('core.article_fetcher.time.time') as mock_time:
                    mock_time.side_effect = [0, 21]  # Immediate timeout

                    with patch('core.article_fetcher.time.sleep'):
                        self.fetcher._prompt_user_skip(title, size_mb)

            # Get stderr output
            stderr_output = sys.stderr.getvalue()

            # Verify no accessibility warning in stderr
            self.assertNotIn('not trusted', stderr_output.lower())
            self.assertNotIn('accessibility', stderr_output.lower())

        finally:
            sys.stderr = old_stderr


class TestPDFSkipConstants(unittest.TestCase):
    """Test that required constants are defined."""

    def test_constants_defined(self):
        """
        Test that LARGE_PDF_THRESHOLD_MB and SKIP_PROMPT_TIMEOUT_SECONDS exist.
        """
        from core.article_fetcher import (
            LARGE_PDF_THRESHOLD_MB,
            SKIP_PROMPT_TIMEOUT_SECONDS
        )

        self.assertEqual(
            LARGE_PDF_THRESHOLD_MB,
            5,
            "PDF threshold should be 5MB"
        )
        self.assertEqual(
            SKIP_PROMPT_TIMEOUT_SECONDS,
            20,
            "Skip prompt timeout should be 20 seconds"
        )


if __name__ == '__main__':
    unittest.main()
