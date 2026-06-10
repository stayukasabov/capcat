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


class TestMarkdownIframeRemoval:
    """M2: <iframe> tags removed."""

    def test_iframe_removed(self):
        content = 'Text\n<iframe src="https://ads.example.com/frame"></iframe>\nEnd'
        result = sanitize(content, mode="markdown")
        assert "<iframe" not in result
        assert "ads.example.com" not in result
        assert "Text" in result
        assert "End" in result


class TestMarkdownEventHandlerRemoval:
    """M3: Inline JS event handlers removed from elements."""

    def test_onload_removed_from_img(self):
        content = '<img src="photo.jpg" onload="track()" alt="photo">'
        result = sanitize(content, mode="markdown")
        assert "onload" not in result
        assert "track()" not in result
        assert "photo.jpg" in result
        assert "<img" in result

    def test_onerror_removed_from_img(self):
        content = '<img src="x" onerror="fetch(\'https://evil.com\')">'
        result = sanitize(content, mode="markdown")
        assert "onerror" not in result
        assert "evil.com" not in result

    def test_onclick_removed_from_div(self):
        content = '<div onclick="sendData()">Click me</div>'
        result = sanitize(content, mode="markdown")
        assert "onclick" not in result
        assert "sendData" not in result
        assert "Click me" in result


class TestMarkdownTrackerImageRemoval:
    """M4: Images from known tracker domains removed."""

    def test_google_analytics_pixel_removed(self):
        content = 'Text\n<img src="https://www.google-analytics.com/collect?v=1&tid=UA-123">\nEnd'
        result = sanitize(content, mode="markdown")
        assert "google-analytics.com" not in result
        assert "Text" in result
        assert "End" in result

    def test_doubleclick_image_removed(self):
        content = '<img src="https://googleads.g.doubleclick.net/pagead/id">'
        result = sanitize(content, mode="markdown")
        assert "doubleclick.net" not in result

    def test_non_tracker_image_preserved(self):
        content = '<img src="https://example.com/photo.jpg" alt="photo">'
        result = sanitize(content, mode="markdown")
        assert "example.com/photo.jpg" in result


class TestMarkdownMetaRefreshRemoval:
    """M5: <meta http-equiv='refresh'> removed."""

    def test_meta_refresh_removed(self):
        content = '<meta http-equiv="refresh" content="0;url=https://tracker.com">\nText'
        result = sanitize(content, mode="markdown")
        assert "meta" not in result.lower() or "refresh" not in result.lower()
        assert "Text" in result


class TestMarkdownPrefetchRemoval:
    """M6: <link rel='prefetch/preload/dns-prefetch'> removed."""

    def test_prefetch_removed(self):
        content = '<link rel="prefetch" href="https://cdn.tracker.com/next.js">\nText'
        result = sanitize(content, mode="markdown")
        assert "prefetch" not in result
        assert "Text" in result

    def test_dns_prefetch_removed(self):
        content = '<link rel="dns-prefetch" href="//analytics.example.com">\nText'
        result = sanitize(content, mode="markdown")
        assert "dns-prefetch" not in result
        assert "Text" in result

    def test_preload_removed(self):
        content = '<link rel="preload" href="https://fonts.googleapis.com/css" as="style">\nText'
        result = sanitize(content, mode="markdown")
        assert "preload" not in result
        assert "Text" in result


class TestMarkdownSvgScriptRemoval:
    """M7: SVG onload/script removed, SVG structure preserved."""

    def test_svg_onload_removed(self):
        content = '<svg onload="fetch(\'https://evil.com\')" width="100"><rect/></svg>'
        result = sanitize(content, mode="markdown")
        assert "onload" not in result
        assert "evil.com" not in result
        assert "<svg" in result
        assert "<rect" in result

    def test_svg_embedded_script_removed(self):
        content = '<svg><script>alert(1)</script><circle r="5"/></svg>'
        result = sanitize(content, mode="markdown")
        assert "<script>" not in result
        assert "alert" not in result
        assert "<circle" in result


class TestMarkdownStyleUrlRemoval:
    """M8: Inline style url() pointing to external domains removed."""

    def test_style_url_external_removed(self):
        content = '<div style="background:url(https://tracker.com/pixel.gif);color:red">Text</div>'
        result = sanitize(content, mode="markdown")
        assert "tracker.com" not in result
        assert "color:red" in result or "color: red" in result
        assert "Text" in result

    def test_style_url_local_preserved(self):
        content = '<div style="background:url(images/bg.png)">Text</div>'
        result = sanitize(content, mode="markdown")
        assert "images/bg.png" in result


class TestMarkdownProtocolRelativeRemoval:
    """M9: Elements with protocol-relative URLs to external domains removed."""

    def test_protocol_relative_script_removed(self):
        content = '<script src="//cdn.tracker.com/track.js"></script>\nText'
        result = sanitize(content, mode="markdown")
        assert "tracker.com" not in result
        assert "Text" in result

    def test_protocol_relative_link_removed(self):
        content = '<link rel="stylesheet" href="//fonts.googleapis.com/css">\nText'
        result = sanitize(content, mode="markdown")
        assert "googleapis.com" not in result
        assert "Text" in result


class TestHeuristic1x1Pixel:
    """Heuristic: 1x1 pixel images detected and removed."""

    def test_1x1_width_height_removed(self):
        content = '<img src="https://unknown.com/img" width="1" height="1">\nText'
        result = sanitize(content, mode="markdown")
        assert "unknown.com" not in result
        assert "Text" in result

    def test_pixel_in_filename_removed(self):
        content = '<img src="https://example.com/pixel.gif">\nText'
        result = sanitize(content, mode="markdown")
        assert "pixel.gif" not in result
        assert "Text" in result

    def test_beacon_in_filename_removed(self):
        content = '<img src="https://example.com/beacon.png">\nText'
        result = sanitize(content, mode="markdown")
        assert "beacon.png" not in result
        assert "Text" in result

    def test_normal_image_preserved(self):
        content = '<img src="https://example.com/photo.jpg" width="800" height="600">'
        result = sanitize(content, mode="markdown")
        assert "photo.jpg" in result


class TestHeuristicQueryHeavyImage:
    """Heuristic: Images with 3+ query params detected as fingerprinting."""

    def test_query_heavy_image_removed(self):
        content = '<img src="https://example.com/img?uid=123&sid=456&cb=789&t=1">\nText'
        result = sanitize(content, mode="markdown")
        assert "uid=123" not in result
        assert "Text" in result

    def test_image_with_few_params_preserved(self):
        content = '<img src="https://example.com/img?w=800&h=600">'
        result = sanitize(content, mode="markdown")
        assert "example.com/img" in result


class TestHeuristicTrackerPath:
    """Heuristic: URLs with tracker path patterns detected."""

    def test_collect_path_removed(self):
        content = '<img src="https://custom-domain.com/collect?v=1&tid=UA-123">\nText'
        result = sanitize(content, mode="markdown")
        assert "custom-domain.com" not in result
        assert "Text" in result

    def test_pixel_path_removed(self):
        content = '<img src="https://metrics.example.com/pixel/view">\nText'
        result = sanitize(content, mode="markdown")
        assert "metrics.example.com" not in result
        assert "Text" in result

    def test_normal_path_preserved(self):
        content = '<img src="https://example.com/images/photo.jpg">'
        result = sanitize(content, mode="markdown")
        assert "photo.jpg" in result


class TestHeuristicHiddenElements:
    """Heuristic: Hidden elements with external URLs removed."""

    def test_display_none_with_external_url_removed(self):
        content = '<div style="display:none"><img src="https://tracker.com/pixel.gif"></div>\nText'
        result = sanitize(content, mode="markdown")
        assert "tracker.com" not in result
        assert "Text" in result

    def test_visibility_hidden_with_external_url_removed(self):
        content = '<img src="https://example.com/track.gif" style="visibility:hidden">\nText'
        result = sanitize(content, mode="markdown")
        assert "track.gif" not in result
        assert "Text" in result
