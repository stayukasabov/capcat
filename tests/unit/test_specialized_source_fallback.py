"""
Regression test: when a specialized source (e.g. Medium) fails,
UnifiedArticleProcessor must fall back to the generic handler
instead of returning (False, None, None).
"""
from unittest.mock import MagicMock, patch


def _make_processor():
    with patch("capcat.core.unified_article_processor.get_source_registry"):
        from capcat.core.unified_article_processor import UnifiedArticleProcessor
        return UnifiedArticleProcessor()


def test_specialized_source_failure_falls_back_to_generic():
    """If specialized source returns success=False, generic handler is tried."""
    processor = _make_processor()

    # Specialized source claims URL but fails
    processor._registry.can_handle_url.return_value = True
    processor._registry.get_source_for_url.return_value = (MagicMock(), "medium")

    generic_result = (True, "Article Title", "/some/folder")

    with (
        patch.object(
            processor,
            "_process_with_specialized_source",
            return_value=(False, None, None),
        ),
        patch.object(
            processor,
            "_process_with_generic_handler",
            return_value=generic_result,
        ) as mock_generic,
    ):
        result = processor.process_article(
            url="https://medium.com/test/article",
            title="Article Title",
            index=0,
            base_folder="/tmp/out",
        )

    mock_generic.assert_called_once()
    assert result == generic_result


def test_specialized_source_success_does_not_call_generic():
    """If specialized source succeeds, generic handler is NOT called."""
    processor = _make_processor()

    processor._registry.can_handle_url.return_value = True
    processor._registry.get_source_for_url.return_value = (MagicMock(), "medium")

    specialized_result = (True, "Article Title", "/some/folder")

    with (
        patch.object(
            processor,
            "_process_with_specialized_source",
            return_value=specialized_result,
        ),
        patch.object(
            processor,
            "_process_with_generic_handler",
        ) as mock_generic,
    ):
        result = processor.process_article(
            url="https://medium.com/test/article",
            title="Article Title",
            index=0,
            base_folder="/tmp/out",
        )

    mock_generic.assert_not_called()
    assert result == specialized_result
