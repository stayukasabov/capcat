#!/usr/bin/env python3
"""
Test for asynchronous PDF downloads to prevent thread pool exhaustion.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

from capcat.core.article_fetcher import NewsSourceArticleFetcher


class TestAsyncPDFDownloads:
    """Test that PDF downloads don't block article processing threads."""

    def test_pdf_downloads_should_not_block_article_threads(self):
        """
        FAILING TEST: PDF downloads currently block article processing threads.
        This should be fixed by making PDF downloads asynchronous.
        """
        # This test demonstrates the current problem and will pass once fixed

        # Mock download_file to simulate slow PDF downloads
        with patch('capcat.core.downloader.download_file') as mock_download:
            def slow_download(url, folder, file_type, enabled):
                if file_type == "document":  # PDFs
                    time.sleep(2)  # Simulate slow PDF download
                    return "files/test.pdf"
                return None

            mock_download.side_effect = slow_download

            # Create fetcher with download_files and download_pdfs enabled (--media path)
            mock_session = Mock()
            mock_config = {"name": "test-source"}
            fetcher = NewsSourceArticleFetcher(mock_config, mock_session, download_files=True, download_pdfs=True)

            # Markdown content with multiple PDF links
            markdown_content = """
            # Test Article
            Here are some PDFs:
            [PDF 1](https://example.com/doc1.pdf)
            [PDF 2](https://example.com/doc2.pdf)
            [PDF 3](https://example.com/doc3.pdf)
            """

            # This should NOT block the calling thread for 6+ seconds
            start_time = time.time()

            result = fetcher._download_pdf_links_from_markdown(
                markdown_content, "/tmp/test_article"
            )

            processing_time = time.time() - start_time

            # CURRENT BEHAVIOR: This will fail because PDF downloads are synchronous
            # DESIRED BEHAVIOR: PDF downloads should be async, so this should take < 1 second
            assert processing_time < 1.0, (
                f"PDF downloads blocked article thread for {processing_time:.1f}s. "
                f"Expected async behavior with <1s processing time."
            )

            # Result should contain placeholder links (not final downloads)
            # This proves PDFs are being processed asynchronously
            assert "files/downloading_" in result, "Should contain placeholder links for async downloads"
            assert "https://example.com/doc1.pdf" not in result, "Original URLs should be replaced"

    def test_thread_pool_not_exhausted_by_pdf_downloads(self):
        """
        Test that multiple articles with PDFs don't exhaust thread pool.
        """
        with patch('capcat.core.downloader.download_file') as mock_download:
            def slow_download(url, folder, file_type, enabled):
                if file_type == "document":
                    time.sleep(1)  # Slow PDF
                    return "files/test.pdf"
                return None

            mock_download.side_effect = slow_download

            # Simulate processing multiple articles with PDFs in thread pool
            def process_article_with_pdfs(article_id):
                mock_session = Mock()
                mock_config = {"name": "test-source"}
                fetcher = NewsSourceArticleFetcher(mock_config, mock_session, download_files=True)

                markdown = f"# Article {article_id}\n[PDF](https://example.com/doc{article_id}.pdf)"
                return fetcher._download_pdf_links_from_markdown(markdown, f"/tmp/article_{article_id}")

            start_time = time.time()

            # Process 4 articles in parallel (simulating thread pool)
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = []
                for i in range(4):
                    future = executor.submit(process_article_with_pdfs, i)
                    futures.append(future)

                # All should complete without excessive delays
                results = [f.result() for f in futures]

            total_time = time.time() - start_time

            # CURRENT BEHAVIOR: Will take ~4 seconds (sequential PDF downloads)
            # DESIRED BEHAVIOR: Should take ~2 seconds (parallel processing)
            assert total_time < 3.0, (
                f"Thread pool exhausted - took {total_time:.1f}s for 4 articles. "
                f"Expected async PDF downloads to prevent blocking."
            )

    def test_pdf_download_failure_does_not_block_article(self):
        """Test that failed PDF downloads don't block article processing."""
        with patch('capcat.core.downloader.download_file') as mock_download:
            # Simulate PDF download failure
            mock_download.side_effect = Exception("Network error")

            mock_session = Mock()
            mock_config = {"name": "test-source"}
            fetcher = NewsSourceArticleFetcher(mock_config, mock_session, download_files=True)

            markdown_content = """
            # Test Article
            [PDF 1](https://example.com/doc1.pdf)
            [PDF 2](https://example.com/doc2.pdf)
            """

            start_time = time.time()

            # Should not block even if downloads fail
            result = fetcher._download_pdf_links_from_markdown(
                markdown_content, "/tmp/test_article"
            )

            processing_time = time.time() - start_time

            # Should complete quickly even with download failures
            assert processing_time < 0.5, f"Failed PDF downloads blocked for {processing_time:.1f}s"

            # Placeholders are placed immediately; failed downloads are resolved later
            assert "files/downloading_" in result or "https://example.com/doc1.pdf" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])