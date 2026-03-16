"""
Regression test for srcset/src URL mismatch between formatter and image_processor.

Bug: _process_images() in formatter.py prefers the highest-resolution URL from
srcset when building markdown image references, but _extract_image_urls() in
image_processor.py ignores srcset and reads only data-src/src. On WordPress
and similar sites the src is a resized variant while srcset contains the full-
resolution URL, so the url_mapping key never matches the URL embedded in the
markdown and the local image path is never substituted.
"""

from capcat.core.formatter import _process_images
from capcat.core.image_processor import ImageProcessor
from bs4 import BeautifulSoup


WORDPRESS_HTML = """
<html><body>
<article>
  <figure>
    <a href="https://example.com/uploads/image-6.png">
      <img
        src="https://example.com/uploads/image-6-1024x768.png"
        srcset="https://example.com/uploads/image-6.png 1536w,
                https://example.com/uploads/image-6-1024x768.png 1024w,
                https://example.com/uploads/image-6-300x225.png 300w"
        alt="Test image"
      />
    </a>
  </figure>
</article>
</body></html>
"""


def _get_markdown_img_url(html: str) -> str:
    """Run _process_images and return the URL embedded in the first ![](url)."""
    soup = BeautifulSoup(html, "html.parser")
    _process_images(soup)
    text = str(soup)
    # Extract URL from first markdown image: ![alt](url)
    import re
    match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", text)
    assert match, f"No markdown image found in: {text}"
    return match.group(1)


def _get_extracted_urls(html: str, base_url: str) -> list:
    """Run _extract_image_urls and return the list of URLs it would download."""
    processor = ImageProcessor()
    img_config = {}  # default config — no srcset handling currently
    return processor._extract_image_urls(html, img_config, base_url)


def test_formatter_uses_srcset_highest_resolution():
    """_process_images must pick the highest-res srcset URL for the markdown."""
    url = _get_markdown_img_url(WORDPRESS_HTML)
    assert url == "https://example.com/uploads/image-6.png", (
        f"Expected full-res srcset URL, got: {url}"
    )


def test_extractor_uses_srcset_highest_resolution():
    """_extract_image_urls must pick the same srcset URL as _process_images."""
    urls = _get_extracted_urls(WORDPRESS_HTML, "https://example.com/")
    assert "https://example.com/uploads/image-6.png" in urls, (
        f"Expected full-res srcset URL in extracted list, got: {urls}"
    )


def test_extractor_and_formatter_agree_on_url():
    """The URL embedded in markdown and the URL downloaded must be identical."""
    markdown_url = _get_markdown_img_url(WORDPRESS_HTML)
    extracted_urls = _get_extracted_urls(WORDPRESS_HTML, "https://example.com/")
    assert markdown_url in extracted_urls, (
        f"Markdown URL '{markdown_url}' not found in extracted URLs {extracted_urls}. "
        "String replacement will silently fail — local image path never substituted."
    )
