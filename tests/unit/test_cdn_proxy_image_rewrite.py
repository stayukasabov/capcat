"""
Regression tests for CDN proxy image URL rewriting.

Bug 1 (clobbering): When multiple images share the same URL path and differ
only in query parameters (Netlify, Next.js, Cloudinary, etc.),
replace_image_urls rewrites ALL image references to the last image processed.

Bug 2 (relative URLs): The formatter may emit relative src paths
(/.netlify/images?url=...) while the url_mapping keys are absolute
(https://host/.netlify/images?url=...). Exact string matching fails
because the strings differ.
"""

from capcat.core.image_processor import ImageProcessor


# Simulates markdown produced by the formatter for a Netlify-proxied article
# with 3 distinct images whose URLs share the same path.
NETLIFY_MARKDOWN = """\
![cover](https://example.com/.netlify/images?url=cover.jpg&w=1440)

Some text here.

![map](https://example.com/.netlify/images?url=map.jpg&w=1440)

More text.

![photo](https://example.com/.netlify/images?url=photo.jpg&w=1440)
"""

NETLIFY_URL_MAPPING = {
    "https://example.com/.netlify/images?url=cover.jpg&w=1440": "image-1.webp",
    "https://example.com/.netlify/images?url=map.jpg&w=1440": "image-2.webp",
    "https://example.com/.netlify/images?url=photo.jpg&w=1440": "image-3.webp",
}


def test_each_image_gets_its_own_local_path():
    """Each CDN proxy URL must map to its own unique local file."""
    result = ImageProcessor.replace_image_urls(NETLIFY_MARKDOWN, NETLIFY_URL_MAPPING)

    assert "![cover](images/image-1.webp)" in result
    assert "![map](images/image-2.webp)" in result
    assert "![photo](images/image-3.webp)" in result


def test_no_image_references_last_file_only():
    """No image reference should be overwritten to the last-processed file."""
    result = ImageProcessor.replace_image_urls(NETLIFY_MARKDOWN, NETLIFY_URL_MAPPING)

    count = result.count("image-3.webp")
    assert count == 1, (
        f"image-3.webp appears {count} times; expected 1. "
        "Fallback regex is clobbering earlier replacements."
    )


# Same class of bug with non-CDN URLs that share a basename
SHARED_BASENAME_MARKDOWN = """\
![a](https://example.com/2024/photo.jpg)

![b](https://example.com/2025/photo.jpg)
"""

SHARED_BASENAME_URL_MAPPING = {
    "https://example.com/2024/photo.jpg": "image-1.jpg",
    "https://example.com/2025/photo.jpg": "image-2.jpg",
}


def test_shared_basename_different_paths():
    """Images with identical filenames in different directories stay distinct."""
    result = ImageProcessor.replace_image_urls(
        SHARED_BASENAME_MARKDOWN, SHARED_BASENAME_URL_MAPPING
    )

    assert "![a](images/image-1.jpg)" in result
    assert "![b](images/image-2.jpg)" in result


def test_shared_basename_no_clobber():
    """Last-processed file must not overwrite the first."""
    result = ImageProcessor.replace_image_urls(
        SHARED_BASENAME_MARKDOWN, SHARED_BASENAME_URL_MAPPING
    )

    count = result.count("image-2.jpg")
    assert count == 1, (
        f"image-2.jpg appears {count} times; expected 1."
    )


# Next.js /_next/image proxy pattern (after _process_images extracts real URL,
# this tests the case where extraction didn't happen and raw proxy URL remains)
NEXTJS_MARKDOWN = """\
![a](https://example.com/_next/image?url=%2Fimg%2Fa.png&w=1080)

![b](https://example.com/_next/image?url=%2Fimg%2Fb.png&w=1080)
"""

NEXTJS_URL_MAPPING = {
    "https://example.com/_next/image?url=%2Fimg%2Fa.png&w=1080": "image-1.png",
    "https://example.com/_next/image?url=%2Fimg%2Fb.png&w=1080": "image-2.png",
}


def test_nextjs_proxy_urls_stay_distinct():
    """Next.js /_next/image proxy URLs must each map to their own file."""
    result = ImageProcessor.replace_image_urls(NEXTJS_MARKDOWN, NEXTJS_URL_MAPPING)

    assert "![a](images/image-1.png)" in result
    assert "![b](images/image-2.png)" in result


# Relative URL in markdown, absolute URL in url_mapping.
# The formatter emits whatever src the page has (often relative),
# but the image downloader resolves to absolute via urljoin.
RELATIVE_NETLIFY_MARKDOWN = """\
![cover](/.netlify/images?url=cover.jpg&w=1440)

![map](/.netlify/images?url=map.jpg&w=1440)

![photo](/.netlify/images?url=photo.jpg&w=1440)
"""

RELATIVE_NETLIFY_URL_MAPPING = {
    "https://example.com/.netlify/images?url=cover.jpg&w=1440": "image-1.webp",
    "https://example.com/.netlify/images?url=map.jpg&w=1440": "image-2.webp",
    "https://example.com/.netlify/images?url=photo.jpg&w=1440": "image-3.webp",
}


def test_relative_urls_replaced_via_path_match():
    """Relative URLs in markdown must match absolute keys via path+query."""
    result = ImageProcessor.replace_image_urls(
        RELATIVE_NETLIFY_MARKDOWN, RELATIVE_NETLIFY_URL_MAPPING
    )

    assert "![cover](images/image-1.webp)" in result
    assert "![map](images/image-2.webp)" in result
    assert "![photo](images/image-3.webp)" in result


def test_relative_urls_no_clobber():
    """Relative URL replacement must not clobber to last image."""
    result = ImageProcessor.replace_image_urls(
        RELATIVE_NETLIFY_MARKDOWN, RELATIVE_NETLIFY_URL_MAPPING
    )

    count = result.count("image-3.webp")
    assert count == 1, (
        f"image-3.webp appears {count} times; expected 1."
    )


# Mixed: some images have relative URLs, some absolute (can happen if
# the page mixes inline and CDN-served images).
MIXED_MARKDOWN = """\
![a](https://example.com/static/hero.jpg)

![b](/.netlify/images?url=detail.jpg&w=800)
"""

MIXED_URL_MAPPING = {
    "https://example.com/static/hero.jpg": "image-1.jpg",
    "https://example.com/.netlify/images?url=detail.jpg&w=800": "image-2.jpg",
}


def test_mixed_absolute_and_relative():
    """Both absolute and relative URLs in the same document get replaced."""
    result = ImageProcessor.replace_image_urls(MIXED_MARKDOWN, MIXED_URL_MAPPING)

    assert "![a](images/image-1.jpg)" in result
    assert "![b](images/image-2.jpg)" in result
