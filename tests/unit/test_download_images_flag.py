"""Regression test — download_images: false must suppress image downloading.

B8: UnifiedMediaProcessor and article_fetcher always downloaded images
regardless of the download_images config flag.
"""
from unittest.mock import MagicMock, patch

from capcat.core.config import FetchNewsConfig, ProcessingConfig


def _config(download_images: bool) -> FetchNewsConfig:
    cfg = FetchNewsConfig()
    cfg.processing = ProcessingConfig(download_images=download_images)
    return cfg


class TestUnifiedMediaProcessorDownloadImagesFlag:
    def test_returns_content_unchanged_when_flag_false(self):
        """process_article_media must return original content when download_images is False."""
        from capcat.core.unified_media_processor import UnifiedMediaProcessor

        cfg = _config(download_images=False)
        with patch("capcat.core.unified_media_processor.get_config", return_value=cfg):
            result = UnifiedMediaProcessor.process_article_media(
                content="# Article\n\nText.",
                html_content="<html><img src='https://example.com/img.png'></html>",
                url="https://example.com/article",
                article_folder="/tmp/test",
                source_name="hn",
                session=MagicMock(),
            )
        assert result == "# Article\n\nText."

    def test_processes_images_when_flag_true(self):
        """process_article_media must attempt image processing when download_images is True."""
        from capcat.core.unified_media_processor import UnifiedMediaProcessor

        cfg = _config(download_images=True)
        mock_processor = MagicMock()
        mock_processor.process_article_images.return_value = {}

        with (
            patch("capcat.core.unified_media_processor.get_config", return_value=cfg),
            patch("capcat.core.unified_media_processor.get_image_processor", return_value=mock_processor),
            patch.object(UnifiedMediaProcessor, "_load_source_config", return_value={}),
        ):
            UnifiedMediaProcessor.process_article_media(
                content="# Article",
                html_content="<html></html>",
                url="https://example.com/article",
                article_folder="/tmp/test",
                source_name="hn",
                session=MagicMock(),
            )

        mock_processor.process_article_images.assert_called_once()
