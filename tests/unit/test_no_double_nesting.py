"""Tests that _process_with_specialized_source does not create an intermediate folder.

After the fix, specialized sources (YouTube, Medium, Substack) receive base_folder
directly and create their own single subfolder inside it. No HN-title intermediate
folder should appear.
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from capcat.core.unified_article_processor import UnifiedArticleProcessor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_processor() -> UnifiedArticleProcessor:
    return UnifiedArticleProcessor()


def _make_mock_specialized_source(tmp_path, content_folder_name="YouTube-Video-Title"):
    """Return a mock specialized source that creates a real subfolder in output_dir."""
    def _fake_fetch(article, output_dir, progress_callback=None):
        content_folder = os.path.join(output_dir, content_folder_name)
        os.makedirs(content_folder, exist_ok=True)
        return True, content_folder

    source_instance = MagicMock()
    source_instance.fetch_article_content.side_effect = _fake_fetch
    return source_instance


# ---------------------------------------------------------------------------
# No intermediate folder
# ---------------------------------------------------------------------------

class TestNoIntermediateFolder:
    """_process_with_specialized_source must not create base_folder/<hn_title>/."""

    def test_no_intermediate_folder_created(self, tmp_path):
        """The single direct child must be named after the content, not the HN post title."""
        content_name = "YouTube-Video-Title"
        hn_title = "Some HN Post Title"
        processor = _make_processor()
        source_instance = _make_mock_specialized_source(tmp_path, content_name)

        with patch.object(
            processor.specialized_manager,
            "can_handle_url",
            return_value=True,
        ):
            with patch.object(
                processor.specialized_manager,
                "get_source_for_url",
                return_value=(source_instance, "youtube"),
            ):
                success, title, folder = processor.process_article(
                    url="https://www.youtube.com/watch?v=abc123",
                    title=hn_title,
                    index=0,
                    base_folder=str(tmp_path),
                )

        assert success is True

        # The single direct child must be the content folder, not an HN-title intermediate
        children = [p for p in tmp_path.iterdir() if p.is_dir()]
        assert len(children) == 1, (
            f"Expected exactly 1 subfolder in base_folder, found: "
            f"{[p.name for p in children]}"
        )
        assert children[0].name == content_name, (
            f"Expected single child to be '{content_name}' (content folder), "
            f"got '{children[0].name}' (likely the HN-title intermediate folder)"
        )

    def test_returned_folder_is_content_folder_not_intermediate(self, tmp_path):
        """process_article must return the folder the specialized source created."""
        content_name = "YouTube-Video-Title"
        processor = _make_processor()
        source_instance = _make_mock_specialized_source(tmp_path, content_name)

        with patch.object(
            processor.specialized_manager,
            "can_handle_url",
            return_value=True,
        ):
            with patch.object(
                processor.specialized_manager,
                "get_source_for_url",
                return_value=(source_instance, "youtube"),
            ):
                success, title, folder = processor.process_article(
                    url="https://www.youtube.com/watch?v=abc123",
                    title="Some HN Post Title",
                    index=0,
                    base_folder=str(tmp_path),
                )

        expected_folder = str(tmp_path / content_name)
        assert folder == expected_folder, (
            f"Expected folder to be the content folder '{expected_folder}', "
            f"got '{folder}'"
        )

    def test_content_is_directly_inside_base_folder(self, tmp_path):
        """Content folder must be at base_folder/content_title/, not base_folder/hn_title/content_title/."""
        content_name = "YouTube-Video-Title"
        hn_title = "Some HN Post Title"
        processor = _make_processor()
        source_instance = _make_mock_specialized_source(tmp_path, content_name)

        with patch.object(
            processor.specialized_manager,
            "can_handle_url",
            return_value=True,
        ):
            with patch.object(
                processor.specialized_manager,
                "get_source_for_url",
                return_value=(source_instance, "youtube"),
            ):
                processor.process_article(
                    url="https://www.youtube.com/watch?v=abc123",
                    title=hn_title,
                    index=0,
                    base_folder=str(tmp_path),
                )

        # Content folder must be a direct child of base_folder
        expected = tmp_path / content_name
        assert expected.exists(), (
            f"Content folder '{content_name}' not found as direct child of base_folder. "
            f"Found: {[p.name for p in tmp_path.iterdir()]}"
        )

        # The hn-title intermediate folder must NOT exist
        from capcat.core.utils import sanitize_filename
        intermediate = tmp_path / sanitize_filename(hn_title)
        assert not intermediate.exists(), (
            f"Intermediate folder '{intermediate.name}' must not be created"
        )

    def test_specialized_source_receives_base_folder(self, tmp_path):
        """The specialized source's fetch_article_content must be called with base_folder."""
        processor = _make_processor()
        source_instance = _make_mock_specialized_source(tmp_path)

        with patch.object(
            processor.specialized_manager,
            "can_handle_url",
            return_value=True,
        ):
            with patch.object(
                processor.specialized_manager,
                "get_source_for_url",
                return_value=(source_instance, "youtube"),
            ):
                processor.process_article(
                    url="https://www.youtube.com/watch?v=abc123",
                    title="Some HN Post Title",
                    index=0,
                    base_folder=str(tmp_path),
                )

        call_args = source_instance.fetch_article_content.call_args
        _, output_dir_arg = call_args[0][0], call_args[0][1]  # article, output_dir
        assert output_dir_arg == str(tmp_path), (
            f"Expected output_dir to be base_folder '{tmp_path}', "
            f"got '{output_dir_arg}'"
        )


# ---------------------------------------------------------------------------
# update_mode backward compatibility
# ---------------------------------------------------------------------------

class TestUpdateModeBackwardCompat:
    """update_mode=True must still create the intermediate folder (backward compat)."""

    def test_update_mode_creates_intermediate_folder(self, tmp_path):
        """In update_mode, the intermediate folder (hn_title) must still be created."""
        from capcat.core.utils import sanitize_filename

        hn_title = "Some HN Post Title"
        processor = _make_processor()
        source_instance = _make_mock_specialized_source(tmp_path)

        # Patch _check_url_validity to return True (valid URL)
        with patch.object(processor, "_check_url_validity", return_value=True):
            with patch.object(processor, "_update_timestamp"):
                with patch.object(
                    processor.specialized_manager,
                    "can_handle_url",
                    return_value=True,
                ):
                    with patch.object(
                        processor.specialized_manager,
                        "get_source_for_url",
                        return_value=(source_instance, "youtube"),
                    ):
                        processor.process_article(
                            url="https://www.youtube.com/watch?v=abc123",
                            title=hn_title,
                            index=0,
                            base_folder=str(tmp_path),
                            update_mode=True,
                        )

        intermediate = tmp_path / sanitize_filename(hn_title)
        assert intermediate.exists(), (
            f"update_mode must create intermediate folder '{intermediate.name}' "
            f"for backward compat with existing article structure"
        )
