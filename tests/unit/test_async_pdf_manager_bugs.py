#!/usr/bin/env python3
"""
Regression tests for async PDF manager bugs:
B1 — placeholder links never updated when downloads take >2 seconds
B2 — updated links use absolute paths instead of relative
"""

import os
import threading
import time

from capcat.core.async_pdf_manager import AsyncPDFManager


class TestStalePlaceholderUpdate:
    """B1 — update_article_with_completed_downloads is called before downloads finish."""

    def test_placeholder_updated_when_download_completes_after_2s(self, tmp_path):
        """
        Placeholder must be replaced even when the PDF download takes >2 seconds.

        Current broken behaviour: the update thread sleeps 2s, checks completed_downloads
        (empty), and exits — placeholder stays in the markdown forever.

        Fixed behaviour: the update thread waits for actual download completion before
        calling update_article_with_completed_downloads.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        try:
            article_folder = tmp_path / "article"
            article_folder.mkdir()
            files_dir = article_folder / "files"
            files_dir.mkdir()

            pdf_url = "https://example.com/paper.pdf"

            # Simulate: manager has queued this URL for this article folder
            manager.extract_and_queue_pdf_links(
                f"[Paper]({pdf_url})", str(article_folder)
            )

            # Write the article markdown with the placeholder
            md_path = article_folder / "Article.md"
            md_path.write_text("[Paper](files/downloading_paper.pdf)\n")

            # Simulate a slow download: complete it after 0.3 seconds
            expected_local = str(files_dir / "paper.pdf")
            (files_dir / "paper.pdf").write_bytes(b"%PDF")

            def complete_after_delay():
                time.sleep(0.3)
                with manager._lock:
                    manager.completed_downloads[pdf_url] = expected_local
                    if pdf_url in manager.active_downloads:
                        manager.active_downloads[pdf_url].set()
                        del manager.active_downloads[pdf_url]

            t = threading.Thread(target=complete_after_delay)
            t.start()
            t.join()

            # wait_for_downloads should pick up the completed event
            queued = manager.get_queued_urls_for_folder(str(article_folder))
            assert pdf_url in queued, "URL should be tracked as queued for this folder"

            manager.wait_for_downloads([pdf_url], timeout=5.0)
            manager.update_article_with_completed_downloads(str(md_path))

            updated = md_path.read_text()
            assert "files/downloading_paper.pdf" not in updated, (
                "Placeholder must be replaced after download completes"
            )
            assert "paper.pdf" in updated, (
                "Updated markdown must contain the actual filename"
            )
        finally:
            manager.stop()

    def test_get_queued_urls_for_folder_returns_queued_urls(self, tmp_path):
        """
        get_queued_urls_for_folder must return the URLs queued for a given folder
        and remove them from internal tracking (to avoid memory leak).
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        try:
            folder = tmp_path / "article"
            folder.mkdir()

            manager.extract_and_queue_pdf_links(
                "[A](https://x.com/a.pdf) [B](https://x.com/b.pdf)",
                str(folder),
            )

            urls = manager.get_queued_urls_for_folder(str(folder))
            assert "https://x.com/a.pdf" in urls
            assert "https://x.com/b.pdf" in urls

            # Second call must return empty (cleaned up)
            urls2 = manager.get_queued_urls_for_folder(str(folder))
            assert urls2 == [], "Queued URLs must be removed after retrieval"
        finally:
            manager.stop()


class TestAbsolutePathInUpdatedMarkdown:
    """B2 — update_article_with_completed_downloads writes absolute paths."""

    def test_updated_link_uses_relative_path(self, tmp_path):
        """
        When a placeholder is replaced with a completed download path,
        the written link must be relative to the markdown file, not absolute.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        try:
            article_folder = tmp_path / "article"
            article_folder.mkdir()
            files_dir = article_folder / "files"
            files_dir.mkdir()

            pdf_url = "https://example.com/paper.pdf"
            absolute_local = str(files_dir / "paper.pdf")
            (files_dir / "paper.pdf").write_bytes(b"%PDF")

            with manager._lock:
                manager.completed_downloads[pdf_url] = absolute_local

            md_path = article_folder / "Article.md"
            md_path.write_text("[Paper](files/downloading_paper.pdf)\n")

            manager.update_article_with_completed_downloads(str(md_path))

            updated = md_path.read_text()
            assert absolute_local not in updated, (
                "Absolute path must not appear in updated markdown"
            )
            assert "files/paper.pdf" in updated, (
                "Relative path must be written instead of absolute path"
            )
        finally:
            manager.stop()

    def test_relative_path_is_relative_to_markdown_dir(self, tmp_path):
        """
        The relative path must be relative to the directory containing the markdown file,
        not to the project root or any other anchor.
        """
        manager = AsyncPDFManager(max_workers=1)
        manager.start()

        try:
            article_folder = tmp_path / "article"
            article_folder.mkdir()
            files_dir = article_folder / "files"
            files_dir.mkdir()

            pdf_url = "https://example.com/report.pdf"
            absolute_local = str(files_dir / "report.pdf")
            (files_dir / "report.pdf").write_bytes(b"%PDF")

            with manager._lock:
                manager.completed_downloads[pdf_url] = absolute_local

            md_path = article_folder / "Article.md"
            md_path.write_text("[Report](files/downloading_report.pdf)\n")

            manager.update_article_with_completed_downloads(str(md_path))

            updated = md_path.read_text()
            # Compute expected relative path from markdown's parent dir
            expected_relative = os.path.relpath(
                absolute_local, str(article_folder)
            )
            assert expected_relative in updated, (
                f"Expected relative path '{expected_relative}' not found in: {updated}"
            )
        finally:
            manager.stop()
