#!/usr/bin/env python3
"""
Tests for PDF global URL deduplication to prevent duplicate downloads.

The AsyncPDFManager should support global deduplication to prevent the same
PDF URL from being downloaded multiple times across different articles.
"""
import os
import tempfile
import pytest

from capcat.core.async_pdf_manager import AsyncPDFManager, shutdown_pdf_manager
from capcat.core.config import PdfConfig


class TestPdfGlobalDeduplication:
    """Tests for global PDF URL deduplication feature."""

    def teardown_method(self):
        shutdown_pdf_manager()

    def test_global_dedup_enabled_prevents_duplicate_downloads(self):
        """
        When global_deduplication=True, same URL in multiple articles should
        only be downloaded once.
        """
        # FAILING TEST: This should pass once global deduplication is implemented

        pdf_config = PdfConfig()
        pdf_config.global_deduplication = True  # New config option

        manager = AsyncPDFManager(pdf_config=pdf_config)
        manager.start()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                article1_path = os.path.join(temp_dir, "article1")
                article2_path = os.path.join(temp_dir, "article2")
                os.makedirs(article1_path)
                os.makedirs(article2_path)

                shared_pdf_url = "https://example.com/shared-paper.pdf"

                # First article should queue the PDF
                content1, count1 = manager.extract_and_queue_pdf_links(
                    f"First article [Paper]({shared_pdf_url})",
                    article1_path
                )

                # Second article should NOT queue the same PDF (global dedup)
                content2, count2 = manager.extract_and_queue_pdf_links(
                    f"Second article [Same Paper]({shared_pdf_url})",
                    article2_path
                )

                # Assertions
                assert count1 == 1, "First article should queue 1 PDF"
                assert count2 == 0, "Second article should queue 0 PDFs (global dedup)"

                # Both articles should still have links, but second should point to shared location
                assert "files/downloading_shared-paper.pdf" in content1
                assert "shared_shared-paper.pdf" in content2  # Should reference shared download

        finally:
            manager.stop()

    def test_global_dedup_disabled_allows_duplicate_downloads(self):
        """
        When global_deduplication=False, same URL in multiple articles should
        be downloaded separately for each article (current behavior).
        """
        pdf_config = PdfConfig()
        pdf_config.global_deduplication = False  # Explicit disable

        manager = AsyncPDFManager(pdf_config=pdf_config)
        manager.start()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                article1_path = os.path.join(temp_dir, "article1")
                article2_path = os.path.join(temp_dir, "article2")
                os.makedirs(article1_path)
                os.makedirs(article2_path)

                shared_pdf_url = "https://example.com/paper.pdf"

                # Both articles should queue the PDF separately
                content1, count1 = manager.extract_and_queue_pdf_links(
                    f"Article 1 [Paper]({shared_pdf_url})",
                    article1_path
                )

                content2, count2 = manager.extract_and_queue_pdf_links(
                    f"Article 2 [Paper]({shared_pdf_url})",
                    article2_path
                )

                # Both should queue (current behavior)
                assert count1 == 1, "First article should queue 1 PDF"
                assert count2 == 1, "Second article should queue 1 PDF"

        finally:
            manager.stop()

    def test_global_dedup_config_defaults_to_false(self):
        """
        Default configuration should have global_deduplication=False
        to maintain backward compatibility.
        """
        pdf_config = PdfConfig()
        assert hasattr(pdf_config, 'global_deduplication'), "PdfConfig should have global_deduplication attribute"
        assert pdf_config.global_deduplication is False, "global_deduplication should default to False"

    def test_global_dedup_same_article_different_urls(self):
        """
        Global deduplication should not affect different PDF URLs
        within the same article.
        """
        pdf_config = PdfConfig()
        pdf_config.global_deduplication = True

        manager = AsyncPDFManager(pdf_config=pdf_config)
        manager.start()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                article_path = os.path.join(temp_dir, "article")
                os.makedirs(article_path)

                # Different URLs should all be queued
                content, count = manager.extract_and_queue_pdf_links(
                    "[Paper1](https://example.com/paper1.pdf) "
                    "[Paper2](https://example.com/paper2.pdf) "
                    "[Paper3](https://example.com/paper3.pdf)",
                    article_path
                )

                assert count == 3, "All 3 different PDFs should be queued"

        finally:
            manager.stop()

    def test_global_dedup_per_article_dedup_still_works(self):
        """
        Global deduplication should not interfere with existing
        per-article deduplication logic.
        """
        pdf_config = PdfConfig()
        pdf_config.global_deduplication = True

        manager = AsyncPDFManager(pdf_config=pdf_config)
        manager.start()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                article_path = os.path.join(temp_dir, "article")
                os.makedirs(article_path)

                # Same URL repeated within one article should only queue once
                content, count = manager.extract_and_queue_pdf_links(
                    "[Paper](https://example.com/paper.pdf) "
                    "[Same Paper](https://example.com/paper.pdf) "
                    "[Paper Again](https://example.com/paper.pdf)",
                    article_path
                )

                assert count == 1, "Only 1 PDF should be queued (per-article dedup)"

        finally:
            manager.stop()