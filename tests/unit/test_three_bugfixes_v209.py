#!/usr/bin/env python3
"""Tests for v2.0.9 bug fixes: PDF size limit, empty comments, fd limit."""
import os
import tempfile
from unittest.mock import patch, MagicMock

from capcat.core.config import PdfConfig


class TestPdfDefaultSizeLimit:
    """PDF default size limit should be 30MB."""

    def test_default_is_30mb(self):
        cfg = PdfConfig()
        assert cfg.max_pdf_size_bytes == 31_457_280


class TestHnEmptyCommentsNotWritten:
    """HN source should not create a comments file when there are no comments."""

    def test_no_file_when_no_comments(self):
        """When comment_ids is empty, no -Comments.md file should be created."""
        from capcat.sources.builtin.custom.hn.source import HnSource

        source = HnSource.__new__(HnSource)
        source.logger = MagicMock()
        source.session = MagicMock()

        with tempfile.TemporaryDirectory() as tmp:
            result = source.fetch_comments(
                comment_url="https://news.ycombinator.com/item?id=123",
                article_title="Test Article",
                article_folder_path=tmp,
                html_mode=False,
                comment_ids=[],
            )

            assert result is False, "Should return False when no comments"

            md_files = [f for f in os.listdir(tmp) if f.endswith(".md")]
            assert len(md_files) == 0, (
                f"No comment files should be created, found: {md_files}"
            )


class TestRaiseFdLimit:
    """CLI should raise file descriptor limit on startup."""

    def test_raise_fd_limit_runs_without_error(self):
        from capcat.cli import _raise_fd_limit
        _raise_fd_limit()

    def test_soft_limit_raised(self):
        import resource
        from capcat.cli import _raise_fd_limit

        _raise_fd_limit()
        soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        assert soft >= 256, f"Soft limit should be at least 256, got {soft}"
