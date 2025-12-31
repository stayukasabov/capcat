"""
Test suite for PDF article handling.

Tests:
- Conditional HTML generation based on generate_html flag
- Streaming download with progress reporting
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.article_fetcher import ArticleFetcher


class ConcretePDFArticleFetcher(ArticleFetcher):
    """Concrete implementation for testing."""

    def should_skip_url(self, url: str, title: str) -> bool:
        return False


class TestPDFHTMLGeneration(unittest.TestCase):
    """Test conditional HTML generation for PDF articles."""

    def setUp(self):
        """Set up test fixtures."""
        mock_session = Mock()
        self.fetcher = ConcretePDFArticleFetcher(
            session=mock_session,
            download_files=False,
            generate_html=False  # HTML generation disabled
        )

    def test_html_not_generated_when_flag_false(self):
        """
        Test that HTML is not generated when generate_html=False.

        Given: ArticleFetcher with generate_html=False
        When: PDF article is processed
        Then: HTMLGenerator should not be called
        """
        title = "Test PDF Article"
        url = "https://example.com/paper.pdf"
        base_folder = "/tmp/test"

        # Mock PDF download
        with patch.object(self.fetcher, '_download_pdf_with_progress', return_value=b"PDF content"):
            # Mock HTMLGenerator to verify it's not called
            with patch('core.html_generator.HTMLGenerator') as mock_html_gen_class:
                with patch('core.article_fetcher.os.makedirs'):
                    with patch('builtins.open', unittest.mock.mock_open()):
                        self.fetcher._handle_pdf_article(
                            title=title,
                            url=url,
                            base_folder=base_folder,
                            progress_callback=None
                        )

                # Verify HTMLGenerator was never instantiated
                mock_html_gen_class.assert_not_called()

    def test_html_generated_when_flag_true(self):
        """
        Test that HTML is generated when generate_html=True.

        Given: ArticleFetcher with generate_html=True
        When: PDF article is processed
        Then: HTMLGenerator should be called
        """
        # Create fetcher with HTML enabled
        mock_session = Mock()
        fetcher_with_html = ConcretePDFArticleFetcher(
            session=mock_session,
            download_files=False,
            generate_html=True  # HTML generation enabled
        )

        title = "Test PDF Article"
        url = "https://example.com/paper.pdf"
        base_folder = "/tmp/test"

        # Mock PDF download
        with patch.object(fetcher_with_html, '_download_pdf_with_progress', return_value=b"PDF content"):
            # Mock HTMLGenerator
            with patch('core.html_generator.HTMLGenerator') as mock_html_gen_class:
                mock_html_gen = Mock()
                mock_html_gen_class.return_value = mock_html_gen

                with patch('core.article_fetcher.os.makedirs'):
                    with patch('builtins.open', unittest.mock.mock_open()):
                        fetcher_with_html._handle_pdf_article(
                            title=title,
                            url=url,
                            base_folder=base_folder,
                            progress_callback=None
                        )

                # Verify HTMLGenerator was instantiated and called
                mock_html_gen_class.assert_called_once()
                mock_html_gen.generate_article_html.assert_called_once()


class TestPDFDownloadProgress(unittest.TestCase):
    """Test streaming download with progress reporting for PDFs."""

    def setUp(self):
        """Set up test fixtures."""
        mock_session = Mock()
        self.fetcher = ConcretePDFArticleFetcher(
            session=mock_session,
            download_files=False
        )

    def test_download_progress_reported(self):
        """
        Test that download progress is reported during streaming download.

        Given: A large PDF file
        When: PDF is downloaded with progress_callback
        Then: Progress callback should be called with download progress
        """
        url = "https://example.com/large.pdf"

        # Mock streaming response
        mock_response = Mock()
        mock_response.headers = {'content-length': '1000000'}  # 1MB

        # Simulate chunks
        chunk_size = 100000  # 100KB chunks
        chunks = [b'x' * chunk_size for _ in range(10)]
        mock_response.iter_content = Mock(return_value=chunks)

        # Mock progress callback
        progress_callback = Mock()

        with patch.object(self.fetcher.session, 'get', return_value=mock_response):
            # This will test the new streaming download method
            self.fetcher._download_pdf_with_progress(
                url=url,
                progress_callback=progress_callback
            )

        # Verify progress was reported
        assert progress_callback.call_count > 0

        # Verify progress values increase
        calls = progress_callback.call_args_list
        progress_values = [call[0][0] for call in calls]

        # Progress should increase
        for i in range(1, len(progress_values)):
            self.assertGreater(progress_values[i], progress_values[i-1])

        # Final progress should be close to 1.0
        self.assertAlmostEqual(progress_values[-1], 1.0, places=1)

    def test_download_without_callback_no_raw_stdout(self):
        """
        Test that download without callback doesn't use raw stdout writes.

        Given: A PDF download without progress_callback
        When: PDF is downloaded
        Then: Should not write to stdout directly (no sys.stdout.write calls)
        """
        url = "https://example.com/paper.pdf"

        # Mock streaming response
        mock_response = Mock()
        mock_response.headers = {'content-length': '500000'}  # 500KB

        # Simulate chunks
        chunks = [b'x' * 50000 for _ in range(10)]
        mock_response.iter_content = Mock(return_value=chunks)

        # Capture stdout to verify no raw writes
        captured_output = io.StringIO()

        with patch.object(self.fetcher.session, 'get', return_value=mock_response):
            with patch('sys.stdout', captured_output):
                # Download without progress_callback
                content = self.fetcher._download_pdf_with_progress(
                    url=url,
                    progress_callback=None
                )

        # Verify content was downloaded
        self.assertEqual(len(content), 500000)

        # Verify no raw stdout writes (captured_output should be empty or only have proper progress API output)
        output = captured_output.getvalue()
        # Should not contain raw progress like "Downloading: X/Y MB"
        self.assertNotIn("Downloading:", output)


if __name__ == '__main__':
    unittest.main()
