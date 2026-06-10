"""Tests for content_sanitizer - archive isolation."""

from capcat.core.content_sanitizer import sanitize


class TestMarkdownScriptRemoval:
    """M1: <script> tags removed from markdown content."""

    def test_script_tag_removed(self):
        content = 'Some text\n<script>alert("xss")</script>\nMore text'
        result = sanitize(content, mode="markdown")
        assert "<script>" not in result
        assert "alert" not in result
        assert "Some text" in result
        assert "More text" in result

    def test_script_tag_with_src_removed(self):
        content = 'Text\n<script src="https://evil.com/track.js"></script>\nEnd'
        result = sanitize(content, mode="markdown")
        assert "<script" not in result
        assert "evil.com" not in result
        assert "Text" in result
        assert "End" in result

    def test_script_tag_multiline_removed(self):
        content = (
            "Before\n"
            "<script type=\"text/javascript\">\n"
            "  var ga = document.createElement('script');\n"
            "  ga.src = 'https://google-analytics.com/ga.js';\n"
            "</script>\n"
            "After"
        )
        result = sanitize(content, mode="markdown")
        assert "<script" not in result
        assert "google-analytics" not in result
        assert "Before" in result
        assert "After" in result
