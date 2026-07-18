"""Tests for json_events html_path capture in launch_web_view."""
from unittest.mock import patch

from capcat.core import json_events
from capcat.core.html_post_processor import launch_web_view


def test_launch_web_view_records_html_path_on_success():
    json_events.pop_html_path()  # reset any leftover state
    with patch("capcat.core.html_post_processor.HTMLPostProcessor") as MockProcessor:
        instance = MockProcessor.return_value
        instance.process_directory_tree.return_value = "file:///tmp/News/index.html"
        instance.launch_browser.return_value = True

        result = launch_web_view("/tmp/News")

    assert result is True
    assert json_events.pop_html_path() == "file:///tmp/News/index.html"


def test_launch_web_view_records_nothing_when_no_index_url():
    json_events.pop_html_path()  # reset
    with patch("capcat.core.html_post_processor.HTMLPostProcessor") as MockProcessor:
        instance = MockProcessor.return_value
        instance.process_directory_tree.return_value = None

        result = launch_web_view("/tmp/News")

    assert result is False
    assert json_events.pop_html_path() is None
