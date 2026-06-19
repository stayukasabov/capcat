"""
Regression test for CDN proxy image URL rewriting.

Bug: When multiple images share the same URL path and differ only in query
parameters (Netlify /.netlify/images, Next.js /_next/image, Cloudinary
/image/fetch, etc.), replace_image_urls rewrites ALL image references to the
last image processed instead of mapping each to its correct local file.

Root cause: _apply_url_patterns has fallback regex patterns that match on
the shared basename ("images") or base-URL-without-query, both of which are
identical across all images from the same CDN proxy endpoint.
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
