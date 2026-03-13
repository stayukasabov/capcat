#!/usr/bin/env python3
"""
HTML to Markdown converter for Capcat.
This module provides functionality to convert HTML content to clean Markdown format.
"""

import re
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment, NavigableString


def _normalize_url(url: str) -> str:
    """Normalize URL by properly handling encoding/decoding issues."""
    if not url or url in ["#", ""]:
        return url

    try:
        # First decode the URL to handle partial encoding
        decoded_url = unquote(url)

        # For reasonable length URLs, return the decoded version
        return decoded_url

    except Exception:
        # If decoding fails, return original URL
        return url


def _create_smart_link(text: str, url: str) -> str:
    """Create a smart link that keeps functionality but has readable display text."""
    if not url or not text:
        return text if text else url

    # If the URL is extremely long (over 200 characters), create a smarter link
    if len(url) > 200:
        # Extract domain for display
        if url.startswith(("http://", "https://")):
            try:
                parts = url.split("/")
                if len(parts) >= 3:
                    domain = parts[2]  # Just the domain part
                    # Create a link with readable text but full URL functionality
                    return f"[{domain} (full URL)]({url})"
            except:
                pass

        # Fallback: use first part of URL as display text
        display_text = url[:50] + "..." if len(url) > 50 else url
        return f"[{display_text}]({url})"

    # For normal URLs, return standard markdown link
    return f"[{text}]({url})"


def format_comment_paragraphs(comment_text: str) -> str:
    """
    Format comment text with proper paragraph breaks and improved readability.
    This is a global utility function for all news sources to improve comment formatting.

    Args:
        comment_text: Raw comment text

    Returns:
        Formatted comment text with proper paragraphs
    """
    if not comment_text:
        return ""

    # Split into sentences and group into paragraphs
    sentences = re.split(r"(?<=[.!?])\s+", comment_text.strip())

    paragraphs = []
    current_paragraph = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        current_paragraph.append(sentence)

        # Start new paragraph after certain patterns or when paragraph gets long
        if (
            len(current_paragraph) >= 3  # Paragraph has 3+ sentences
            and (
                sentence.endswith(".")
                or sentence.endswith("!")
                or sentence.endswith("?")
            )
            and len(" ".join(current_paragraph)) > 150
        ):  # Paragraph is reasonably long

            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []

    # Add remaining sentences as final paragraph
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    # Join paragraphs with double line breaks for proper markdown formatting
    formatted_text = "\n\n".join(paragraphs)

    # Clean up any remaining formatting issues
    formatted_text = re.sub(
        r"\n{3,}", "\n\n", formatted_text
    )  # Max 2 consecutive newlines
    formatted_text = re.sub(
        r" {2,}", " ", formatted_text
    )  # Remove multiple spaces

    # Return properly formatted comment text without additional processing
    return formatted_text.strip()


def html_to_markdown(html_content: str, base_url: str = None) -> str:
    """Convert HTML content to clean markdown format."""
    try:
        # Parse the HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Store base_url in soup for use in other functions
        if base_url:
            soup.base_url = base_url

        # Remove script, style, and other unwanted elements
        for tag in soup(
            ["script", "style", "nav", "header", "footer", "aside", "button"]
        ):
            tag.decompose()

        # Enhanced cleanup for InfoQ and other sources
        _enhanced_cleanup(soup)

        # Process images first to ensure proper Markdown syntax
        _process_images(soup)

        # Process links to ensure proper Markdown syntax
        _process_links(soup)

        # Process code blocks to ensure proper formatting
        _process_code_blocks(soup)

        # Process audio and video elements to preserve them
        _process_media_elements(soup)

        # Convert the entire soup to markdown
        markdown_content = _convert_element(soup)

        # Clean up excessive whitespace and newlines
        markdown_content = re.sub(
            r" {2,}", " ", markdown_content
        )  # Multiple spaces to single
        markdown_content = re.sub(
            r"\n{4,}", "\n\n\n", markdown_content
        )  # Limit excessive newlines
        # Trim leading and trailing whitespace from the entire content, not from each line
        markdown_content = markdown_content.strip()

        # Spacing is handled properly by _convert_element, no need for additional processing

        # Fix common issues with code blocks
        markdown_content = re.sub(
            r"```\s*\n\s*```", "", markdown_content
        )  # Remove empty code blocks
        markdown_content = re.sub(
            r"```(\w+)\s*\n\s*```", "", markdown_content
        )  # Remove empty code blocks with language

        # Fix stray characters before code blocks
        markdown_content = re.sub(
            r"y\s*```", "```", markdown_content
        )  # Remove stray 'y' before code blocks

        # Fix image rendering issues - ensure Markdown images are properly formatted
        markdown_content = re.sub(
            r"\[!\$\$(.*?)\$\$\$\((.*?)\)\]\((.*?)\)",
            r"![\1](\3)",
            markdown_content,
        )

        # Clean up indented links that might be interpreted as code blocks
        # Pattern: lines starting with tabs/spaces followed by markdown link
        markdown_content = re.sub(
            r"^\s{4,}(\[.*?\]\(https?://.*?\))",
            r"\1",
            markdown_content,
            flags=re.MULTILINE,
        )

        # Return properly converted markdown without additional processing
        return markdown_content.strip()

    except Exception as e:
        # If conversion fails, return cleaned text
        import traceback
        print(f"Warning: HTML to Markdown conversion failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        fallback_content = "\n".join(lines)
        # Return fallback content without additional processing
        return fallback_content


def _parse_srcset(srcset: str) -> str:
    """Parse srcset attribute and return the highest resolution image URL."""
    if not srcset:
        return ""

    # srcset format: "url1 width1, url2 width2, url3 width3"
    # Example: "image-480.jpg 480w, image-800.jpg 800w, image-1200.jpg 1200w"
    entries = [entry.strip() for entry in srcset.split(",")]

    best_url = ""
    max_width = 0

    for entry in entries:
        parts = entry.rsplit(
            " ", 1
        )  # Split from right to separate URL from descriptor
        if len(parts) == 2:
            url, descriptor = parts
            url = url.strip()
            descriptor = descriptor.strip()

            # Extract width from descriptor (e.g., "800w" -> 800)
            if descriptor.endswith("w"):
                try:
                    width = int(descriptor[:-1])
                    if width > max_width:
                        max_width = width
                        best_url = url
                except ValueError:
                    continue
            elif descriptor.endswith("x"):
                # Handle pixel density descriptors (e.g., "2x")
                try:
                    density = float(descriptor[:-1])
                    # Treat higher density as preference when no width-based entries
                    if not best_url or max_width == 0:
                        best_url = url
                except ValueError:
                    continue
        elif len(parts) == 1:
            # No descriptor, just URL - use as fallback
            if not best_url:
                best_url = parts[0].strip()

    return best_url


def _process_images(soup):
    """Process img tags to ensure proper Markdown syntax, filtering out broken images."""
    images = soup.find_all("img")
    for img in images:
        # Skip if img is None or has None attrs (malformed HTML)
        if img is None or not hasattr(img, 'attrs') or img.attrs is None:
            continue

        src = img.get("src", "")

        # Check for srcset attribute for responsive images (prioritize highest resolution)
        srcset = img.get("srcset", "")
        if srcset:
            best_src = _parse_srcset(srcset)
            if best_src:
                src = best_src

        if not src:
            # Try data-src for lazy-loaded images
            src = img.get("data-src", "")
        if not src:
            # Try data-lazy for lazy-loaded images
            src = img.get("data-lazy", "")

        alt = img.get("alt", "image")
        if src:
            # Handle Next.js optimized images by extracting the real URL
            if src.startswith("/_next/image?url="):
                import urllib.parse

                # Extract the actual image URL from Next.js wrapper
                parsed = urllib.parse.parse_qs(src.split("?", 1)[1])
                if "url" in parsed:
                    real_url = urllib.parse.unquote(parsed["url"][0])
                    src = real_url

            # Check if this looks like a broken image URL or other problematic patterns
            if _is_broken_image_url(src):
                # Skip broken images entirely instead of creating broken markdown
                img.decompose()
                continue

            # Replace the img tag with a Markdown image
            markdown_img = f"![{alt}]({src})"
            img.replace_with(markdown_img)
        else:
            # Remove img tag if no src
            img.decompose()


def _is_broken_image_url(url: str) -> bool:
    """Check if an image URL is likely to be broken or undownloadable."""
    if not url:
        return True

    # Common broken image patterns
    broken_patterns = [
        "/_next/image?url=",  # Next.js optimized images that won't work externally
        "data:image/svg+xml,",  # Inline SVG data that's often just placeholders
        "/assets/images/placeholder",  # Common placeholder patterns
        "/img/placeholder",
        "placeholder.svg",
        "loading.gif",
        "/static/images/default",
        "grey-placeholder",  # Grey placeholder images from BBC and other sources
        "placeholder.png",  # Generic placeholder images
    ]

    # Check for broken patterns
    url_lower = url.lower()
    for pattern in broken_patterns:
        if pattern in url_lower:
            return True

    # Check for relative URLs that won't resolve properly
    if url.startswith("/") and not url.startswith("//"):
        # This is a relative URL - might be problematic depending on context
        # For now, let the article fetcher handle these
        pass

    return False


def _process_links(soup):
    """Process a tags to ensure proper Markdown syntax."""
    links = soup.find_all("a")
    # Get base_url if available
    base_url = getattr(soup, "base_url", None)

    for link in links:
        # Skip if link is None or has None attrs (malformed HTML)
        if link is None or not hasattr(link, 'attrs') or link.attrs is None:
            continue

        href = link.get("href", "#")
        text = link.get_text()

        # Clean up text by normalizing whitespace and removing excessive indentation
        if text:
            # Replace multiple whitespace characters (including newlines) with single spaces
            text = " ".join(text.split())
            # Remove leading/trailing whitespace
            text = text.strip()

        # Convert relative URLs to absolute URLs
        if base_url and href.startswith("/"):
            # Convert relative URLs to absolute
            from urllib.parse import urljoin

            href = urljoin(base_url, href)
        elif (
            base_url
            and href.startswith("./")
            or (
                not href.startswith(
                    ("http://", "https://", "#", "mailto:", "javascript:")
                )
                and href != ""
            )
        ):
            # Handle relative paths
            from urllib.parse import urljoin

            href = urljoin(base_url, href.lstrip("./"))

        # Normalize the URL to fix encoding issues
        href = _normalize_url(href)

        if text and href:
            # Create a smart link that handles long URLs properly
            markdown_link = _create_smart_link(text, href)
            link.replace_with(markdown_link)
        elif text:
            # If no href, just keep the text
            link.replace_with(text)
        else:
            # Remove link if no text
            link.decompose()


def _process_code_blocks(soup):
    """Process pre and code tags to ensure proper Markdown code block formatting."""
    # Process <pre><code> blocks
    pre_tags = soup.find_all("pre")
    for pre in pre_tags:
        # Skip if pre is None or has None attrs (malformed HTML)
        if pre is None or not hasattr(pre, 'attrs') or pre.attrs is None:
            continue

        # Get the raw text content
        code_text = pre.get_text()

        # Try to detect the language if possible
        language = ""
        code_class = pre.get("class", [])
        for cls in code_class:
            if cls.startswith("brush:"):
                language = cls.split(":")[1]
                break
            elif cls.startswith("language-"):
                language = cls.split("-")[1]
                break

        # Format as a code block
        if language:
            markdown_code = f"\n```{language}\n{code_text.strip()}\n```\n"
        else:
            markdown_code = f"\n```\n{code_text.strip()}\n```\n"

        # Replace the pre tag with the Markdown code block
        pre.replace_with(markdown_code)

    # Process standalone <code> tags (inline code)
    code_tags = soup.find_all("code")
    for code in code_tags:
        # Skip if code is None or has None attrs (malformed HTML)
        if code is None or not hasattr(code, 'attrs') or code.attrs is None:
            continue

        # Check if this code tag is already inside a pre tag (processed above)
        parent = code.parent
        if parent and parent.name == "pre":
            # Skip if already processed
            continue

        # Get the raw text content
        code_text = code.get_text()

        # For inline code, we don't need language specification
        # Special handling for single characters that shouldn't be in code blocks
        if len(code_text) == 1 and code_text in ["x", "y"]:
            markdown_code = code_text
        else:
            markdown_code = f"`{code_text}`"

        # Replace the code tag with the Markdown inline code
        code.replace_with(markdown_code)


def _process_media_elements(soup):
    """Process audio and video elements to preserve them in the output."""
    # Process audio elements - preserve them as HTML with better formatting
    audio_elements = soup.find_all("audio")
    for audio in audio_elements:
        # Skip if audio is None or has None attrs (malformed HTML)
        if audio is None or not hasattr(audio, 'attrs') or audio.attrs is None:
            continue

        # Add a class to identify processed audio elements
        if audio.get("class"):
            audio["class"] = audio.get("class", []) + ["processed-audio"]
        else:
            audio["class"] = ["processed-audio"]

        # Ensure the audio element has controls
        audio["controls"] = ""

        # Process source elements within audio
        source_elements = audio.find_all("source")
        for source in source_elements:
            # Skip if source is None or has None attrs (malformed HTML)
            if source is None or not hasattr(source, 'attrs') or source.attrs is None:
                continue

            # Ensure source elements have proper attributes
            if not source.get("type"):
                # Try to infer type from src extension
                src = source.get("src", "")
                if src.endswith(".mp3"):
                    source["type"] = "audio/mpeg"
                elif src.endswith(".wav"):
                    source["type"] = "audio/wav"
                elif src.endswith(".ogg"):
                    source["type"] = "audio/ogg"
                elif src.endswith(".flac"):
                    source["type"] = "audio/flac"

    # Process video elements - preserve them as HTML with better formatting
    video_elements = soup.find_all("video")
    for video in video_elements:
        # Skip if video is None or has None attrs (malformed HTML)
        if video is None or not hasattr(video, 'attrs') or video.attrs is None:
            continue

        # Add a class to identify processed video elements
        if video.get("class"):
            video["class"] = video.get("class", []) + ["processed-video"]
        else:
            video["class"] = ["processed-video"]

        # Ensure the video element has controls
        video["controls"] = ""

        # Set default dimensions if not present
        if not video.get("width"):
            video["width"] = "1280"
        if not video.get("height"):
            video["height"] = "720"

        # Process source elements within video
        source_elements = video.find_all("source")
        for source in source_elements:
            # Skip if source is None or has None attrs (malformed HTML)
            if source is None or not hasattr(source, 'attrs') or source.attrs is None:
                continue

            # Ensure source elements have proper attributes
            if not source.get("type"):
                # Try to infer type from src extension
                src = source.get("src", "")
                if src.endswith(".mp4"):
                    source["type"] = "video/mp4"
                elif src.endswith(".webm"):
                    source["type"] = "video/webm"
                elif src.endswith(".ogg"):
                    source["type"] = "video/ogg"
                elif src.endswith(".mov"):
                    source["type"] = "video/quicktime"

    # Process media placeholders that might be used by InfoQ
    # Look for divs or spans that indicate media content
    media_placeholders = soup.find_all(
        ["div", "span"], class_=re.compile(r".*(audio|video|media).*", re.I)
    )

    # Track if we've already added media notes to avoid duplicates
    has_video_note = False
    has_audio_note = False

    for placeholder in media_placeholders:
        # Skip if placeholder is None or has None attrs (malformed HTML)
        if placeholder is None or not hasattr(placeholder, 'attrs') or placeholder.attrs is None:
            continue

        # If it's a placeholder for media content, add a note
        classes = placeholder.get("class", [])
        element_id = (placeholder.get("id") or "").lower()
        if (
            any("audio" in cls.lower() for cls in classes)
            or "audio" in element_id
        ):
            if not has_audio_note:
                # Replace with a note about audio content
                note = soup.new_tag("p")
                note.string = "Audio content available in the original article."
                placeholder.replace_with(note)
                has_audio_note = True
            else:
                # Remove duplicate audio placeholders
                placeholder.decompose()
        elif (
            any("video" in cls.lower() for cls in classes)
            or "video" in element_id
        ):
            if not has_video_note:
                # Replace with a note about video content
                note = soup.new_tag("p")
                note.string = "Video content available in the original article."
                placeholder.replace_with(note)
                has_video_note = True
            else:
                # Remove duplicate video placeholders
                placeholder.decompose()


def _convert_element(element, depth=0, max_depth=50) -> str:
    """Recursively convert an HTML element to Markdown with improved formatting preservation."""
    # Prevent infinite recursion and hangs
    if depth > max_depth:
        return ""

    # Handle None elements (can occur with malformed HTML)
    if element is None:
        return ""

    if isinstance(element, NavigableString):
        # Skip comment nodes
        if isinstance(element, Comment):
            return ""
        # For plain text, normalize whitespace but preserve intentional line breaks
        text = str(element)
        # Only normalize excessive whitespace, not all whitespace
        text = re.sub(r" {2,}", " ", text)  # Multiple spaces to single
        return text

    # If it's already a string (from our processing), return it
    if isinstance(element, str):
        return element

    # Special handling for media elements - preserve them as HTML
    if element.name in ["audio", "video"]:
        # Return the HTML as-is for media elements
        return str(element)

    markdown = ""

    # Process children first with depth protection
    children_content = ""
    child_count = 0
    for child in element.children:
        # Limit number of children processed to prevent hangs
        if child_count > 1000:
            break
        child_md = _convert_element(child, depth + 1, max_depth)
        children_content += child_md
        child_count += 1

    # Handle different tag types with improved formatting preservation
    if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        # Preserve header hierarchy with proper spacing
        level = int(element.name[1])
        header_prefix = "#" * level
        content = children_content.strip()
        if content:
            # Add proper spacing before headers (except h1 at start)
            prefix = "\n\n" if level > 1 or depth > 0 else ""
            markdown = f"{prefix}{header_prefix} {content}\n\n"
        else:
            markdown = ""
    elif element.name == "p":
        # Preserve paragraph content with proper spacing
        content = children_content.strip()
        if content:
            # Check if this paragraph contains only formatting elements
            if element.get_text().strip():
                markdown = f"{content}\n\n"
            else:
                markdown = ""
        else:
            markdown = ""
    elif element.name == "br":
        markdown = "\n"
    elif element.name == "hr":
        markdown = "\n---\n\n"
    elif element.name == "strong" or element.name == "b":
        content = children_content.strip()
        if content:
            markdown = f"**{content}**"
        else:
            markdown = ""
    elif element.name == "em" or element.name == "i":
        content = children_content.strip()
        if content:
            markdown = f"*{content}*"
        else:
            markdown = ""
    elif element.name == "ul":
        # Improved unordered list handling with better spacing
        items = _process_list_items(element, "-", depth)
        if items:
            prefix = "\n" if depth == 0 else ""
            suffix = "\n" if depth == 0 else ""
            markdown = f"{prefix}{chr(10).join(items)}{suffix}"
        else:
            markdown = ""
    elif element.name == "ol":
        # Improved ordered list handling with preserved numbering
        start_num = int(element.get("start", 1))
        items = _process_list_items(element, "number", depth, start_num)
        if items:
            prefix = "\n" if depth == 0 else ""
            suffix = "\n" if depth == 0 else ""
            markdown = f"{prefix}{chr(10).join(items)}{suffix}"
        else:
            markdown = ""
    elif element.name == "li":
        # This is handled in ul/ol processing, but preserve content
        markdown = children_content.rstrip()
    elif element.name == "blockquote":
        # Improved blockquote handling that preserves formatting
        content = children_content.strip()
        if content:
            markdown = _format_blockquote(content)
        else:
            markdown = ""
    elif (
        element.name == "code"
        and element.parent
        and element.parent.name != "pre"
    ):
        # Inline code - preserve exactly
        content = element.get_text()
        if content and len(content.strip()) > 0:
            # Don't wrap single characters or very short strings unnecessarily
            if len(content.strip()) == 1 and content.strip() in [
                "x",
                "y",
                "z",
            ]:
                markdown = content
            else:
                markdown = f"`{content}`"
        else:
            markdown = ""
    elif element.name == "pre":
        # This should be handled by _process_code_blocks, but ensure we don't double-process
        markdown = children_content
    elif element.name in ["table", "thead", "tbody", "tr", "th", "td"]:
        # Basic table support - preserve structure
        markdown = _convert_table_element(element, children_content)
    elif element.name == "div":
        # For divs, preserve content but be smarter about spacing
        content = children_content.strip()
        if content:
            # Only add spacing if this div contains significant content
            if element.get_text().strip():
                markdown = f"\n{content}\n" if depth == 0 else content
            else:
                markdown = content
        else:
            markdown = ""
    elif element.name in ["span", "a"]:
        # For inline elements, just preserve their content
        markdown = children_content
    else:
        # For other tags, just process their children
        markdown = children_content

    # Clean up excessive whitespace while preserving intentional formatting
    if markdown:
        # Limit excessive newlines but don't remove all spacing
        markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)
        # Clean up spaces at line endings
        markdown = re.sub(r" +\n", "\n", markdown)

    return markdown


def _process_list_items(list_element, marker_type, depth, start_num=1):
    """Process list items with improved formatting and nesting support."""
    items = []
    indent = "  " * depth  # 2 spaces per nesting level

    li_elements = list_element.find_all("li", recursive=False)
    for i, li in enumerate(li_elements):
        # Skip if li is None or has None attrs (malformed HTML)
        if li is None or not hasattr(li, 'attrs') or li.attrs is None:
            continue

        # Get the list item content
        item_content = _convert_element(li, depth + 1, 50).strip()

        if not item_content:
            continue

        # Create the appropriate marker
        if marker_type == "number":
            marker = f"{start_num + i}."
        else:
            marker = "-"

        # Handle nested lists within this item
        nested_lists = li.find_all(["ul", "ol"], recursive=False)
        if nested_lists:
            # Process nested content more carefully
            main_content = ""
            for child in li.children:
                if hasattr(child, "name") and child.name in ["ul", "ol"]:
                    # Skip nested lists - they'll be processed separately
                    continue
                else:
                    main_content += _convert_element(child, depth + 1, 50)

            # Clean up the main content
            main_content = main_content.strip()

            # Add the main list item
            if main_content:
                items.append(f"{indent}{marker} {main_content}")

            # Process nested lists
            for nested_list in nested_lists:
                # Skip if nested_list is None or has None attrs (malformed HTML)
                if nested_list is None or not hasattr(nested_list, 'attrs') or nested_list.attrs is None:
                    continue

                nested_marker = "number" if nested_list.name == "ol" else "-"
                nested_start = (
                    int(nested_list.get("start", 1))
                    if nested_list.name == "ol"
                    else 1
                )
                nested_items = _process_list_items(
                    nested_list, nested_marker, depth + 1, nested_start
                )
                for nested_item in nested_items:
                    items.append(
                        f"  {nested_item}"
                    )  # Extra indent for nested items
        else:
            # Handle multi-line content within list items
            content_lines = item_content.split("\n")
            first_line = content_lines[0] if content_lines else ""
            remaining_lines = (
                content_lines[1:] if len(content_lines) > 1 else []
            )

            # Add the first line with the marker
            if first_line:
                items.append(f"{indent}{marker} {first_line}")

            # Add remaining lines with proper indentation
            for line in remaining_lines:
                if line.strip():
                    items.append(
                        f"{indent}   {line}"
                    )  # Align with content, not marker

    return items


def _format_blockquote(content):
    """Format blockquote content with proper markdown quoting."""
    if not content.strip():
        return ""

    lines = content.split("\n")
    quoted_lines = []

    for line in lines:
        if line.strip():
            quoted_lines.append(f"> {line}")
        else:
            quoted_lines.append(">")  # Empty quote line

    if quoted_lines:
        return f"\n{chr(10).join(quoted_lines)}\n\n"
    else:
        return ""


def _convert_table_element(element, children_content):
    """Convert table elements to markdown table format."""
    if element.name == "table":
        # For now, just return the content as-is with some formatting
        # Full table conversion would be more complex
        return f"\n{children_content}\n"
    elif element.name in ["thead", "tbody"]:
        return children_content
    elif element.name == "tr":
        # Table row - add line break
        return f"{children_content}\n"
    elif element.name in ["th", "td"]:
        # Table cell - add separator
        return f"{children_content} | "
    else:
        return children_content


def _enhanced_cleanup(soup):
    """Enhanced cleanup for InfoQ and other sources."""
    # Only apply specific cleanup if we detect InfoQ content
    base_url = getattr(soup, "base_url", "") or ""
    is_infoq = "infoq.com" in base_url.lower()

    if not is_infoq:
        # For non-InfoQ sites, only do minimal cleanup
        elements_to_remove = []

        # Only remove clearly tracking elements
        for elem in soup.find_all(
            class_=re.compile(r".*google-analytics.*", re.I)
        ):
            elements_to_remove.append(elem)

        for elem in elements_to_remove:
            elem.decompose()
        return

    # InfoQ-specific cleanup (original code)
    # Remove InfoQ-specific elements
    # Remove homepage links
    elements_to_remove = []
    for elem in soup.find_all(text=re.compile(r".*InfoQ Homepage.*", re.I)):
        if elem.parent:
            elements_to_remove.append(elem.parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove site markers
    elements_to_remove = []
    for elem in soup.find_all(
        text=re.compile(r".*SITE START.*|.*CONTENT START.*", re.I)
    ):
        if elem.parent:
            elements_to_remove.append(elem.parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove branding links - both by href and by text
    elements_to_remove = []
    for elem in soup.find_all("a", href=re.compile(r".*/int/bt/.*", re.I)):
        elements_to_remove.append(elem)
    for elem in soup.find_all("a", text=re.compile(r".*BT.*", re.I)):
        elements_to_remove.append(elem)
    for elem in soup.find_all(text=re.compile(r".*\[BT\].*", re.I)):
        # Remove the parent element containing [BT]
        if elem.parent:
            elements_to_remove.append(elem.parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove navigation text
    elements_to_remove = []
    for elem in soup.find_all(
        text=re.compile(r".*Login Register About InfoQ.*", re.I)
    ):
        if elem.parent:
            elements_to_remove.append(elem.parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove tracking elements
    elements_to_remove = []
    for elem in soup.find_all(
        class_=re.compile(r".*google-analytics.*", re.I)
    ):
        elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove Google Tag Manager elements
    # Remove script tags with Google Tag Manager
    elements_to_remove = []
    for elem in soup.find_all("script"):
        if elem.string and (
            "Google Tag Manager" in elem.string
            or "gtag" in elem.string
            or "ga(" in elem.string
            or "googletag" in elem.string
            or "GTM-" in elem.string
        ):
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove noscript Google Tag Manager elements
    elements_to_remove = []
    for elem in soup.find_all("noscript"):
        # Check both text content and src attributes for GTM references
        if (
            elem.find(text=re.compile(r".*Google Tag Manager.*", re.I))
            or "googletagmanager.com" in str(elem)
            or elem.find(
                attrs={"src": re.compile(r".*googletagmanager.com.*", re.I)}
            )
        ):
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove iframe elements related to tracking
    elements_to_remove = []
    for elem in soup.find_all("iframe"):
        src = elem.get("src", "")
        if (
            "googletagmanager.com" in src
            or "google-analytics.com" in src
            or "doubleclick.net" in src
        ):
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove link elements related to tracking
    elements_to_remove = []
    for elem in soup.find_all("link"):
        href = elem.get("href", "")
        if "googletagmanager.com" in href or "google-analytics.com" in href:
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove conditional comments (IE specific code)
    # Remove elements within IE conditional comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    parents_to_remove = []
    for comment in comments:
        if comment.strip().startswith("[if") and (
            "IE" in comment or "lt IE" in comment
        ):
            # Find the parent element that contains this comment
            parent = comment.parent
            if parent:
                parents_to_remove.append(parent)

    # Remove the parents after collecting them to avoid modifying the soup during iteration
    for parent in parents_to_remove:
        parent.decompose()

    # Also remove conditional comment blocks specifically
    # Find comment strings that contain IE conditional comments and remove their parents
    elements_to_remove = []
    for elem in soup.find_all(
        string=re.compile(r".*\[if\s*.*IE.*\]>.*", re.I)
    ):
        parent = elem.parent if hasattr(elem, "parent") else None
        if parent:
            elements_to_remove.append(parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for parent in elements_to_remove:
        parent.decompose()

    # Remove any script tags that contain conditional IE code
    elements_to_remove = []
    for elem in soup.find_all("script"):
        if elem.string and (
            "createElement" in elem.string
            and (
                "header" in elem.string
                or "nav" in elem.string
                or "main" in elem.string
                or "section" in elem.string
                or "article" in elem.string
                or "aside" in elem.string
                or "footer" in elem.string
            )
        ):
            # Check if this looks like the IE8 shim script
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove any remaining tracking-related elements
    tracking_selectors = [
        'script[src*="googletagmanager.com"]',
        'script[src*="google-analytics.com"]',
        'script[src*="doubleclick.net"]',
        'iframe[src*="googletagmanager.com"]',
        'iframe[src*="google-analytics.com"]',
        'iframe[src*="doubleclick.net"]',
    ]

    elements_to_remove = []
    for selector in tracking_selectors:
        for elem in soup.select(selector):
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Remove elements with tracking-related IDs or classes
    tracking_patterns = re.compile(
        r".*(gtm|google.*tag.*manager|google.*analytics|doubleclick|track|analytic).*",
        re.I,
    )
    elements_to_remove = []
    for elem in soup.find_all(attrs={"id": tracking_patterns}):
        elements_to_remove.append(elem)
    for elem in soup.find_all(attrs={"class": tracking_patterns}):
        elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Enhanced cleanup for dnes.dir.bg and similar Bulgarian sites
    # Remove IE conditional comments more thoroughly
    elements_to_remove = []
    for elem in soup.find_all(
        text=re.compile(r".*\[if.*lt.*IE.*\].*\[endif\].*", re.I)
    ):
        parent = elem.parent if hasattr(elem, "parent") else None
        if parent:
            elements_to_remove.append(parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for parent in elements_to_remove:
        parent.decompose()

    # Remove Google Tag Manager text content that might appear in the body
    elements_to_remove = []
    for elem in soup.find_all(
        text=re.compile(
            r".*Google Tag Manager.*|.*End Google Tag Manager.*", re.I
        )
    ):
        parent = elem.parent if hasattr(elem, "parent") else None
        if parent:
            elements_to_remove.append(parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for parent in elements_to_remove:
        parent.decompose()

    # Remove stray "html" text that sometimes appears
    elements_to_remove = []
    for elem in soup.find_all(text=re.compile(r"^\s*html\s*$", re.I)):
        parent = elem.parent if hasattr(elem, "parent") else None
        if parent:
            elements_to_remove.append(parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for parent in elements_to_remove:
        parent.decompose()

    # Remove author sections
    elements_to_remove = []
    for elem in soup.find_all(text=re.compile(r".*About the Author.*", re.I)):
        # Find the parent container and remove it
        parent = elem.parent
        if parent:
            # Check if this is a heading
            if parent.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                # Remove the heading and its parent container
                container = parent.parent
                if container and container.name in ["div", "section"]:
                    elements_to_remove.append(container)
                else:
                    elements_to_remove.append(parent)
            else:
                # Remove the element itself and its siblings that might be part of the bio
                container = parent.parent
                if container and container.name in ["div", "section"]:
                    elements_to_remove.append(container)
                else:
                    elements_to_remove.append(parent)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()

    # Also look for paragraphs containing author bio text
    elements_to_remove = []
    for elem in soup.find_all(
        "p", text=re.compile(r".*software engineer.*", re.I)
    ):
        parent = elem.parent
        if parent and parent.name in ["div", "section"]:
            elements_to_remove.append(parent)
        else:
            elements_to_remove.append(elem)

    # Remove the elements after collecting them to avoid modifying the soup during iteration
    for elem in elements_to_remove:
        elem.decompose()
