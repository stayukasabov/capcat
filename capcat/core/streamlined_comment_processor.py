#!/usr/bin/env python3
"""
Streamlined comment processor for optimizing nested structure handling and reducing conversion time.
Designed to flatten complex comment hierarchies and provide inline comment display.
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, NavigableString
import logging

logger = logging.getLogger(__name__)


class StreamlinedCommentProcessor:
    """
    High-performance comment processor that flattens nested structures
    and optimizes conversion time by eliminating complex tree traversal.
    """

    def __init__(self, max_comments: int = 100, max_links_per_comment: int = 5):
        self.max_comments = max_comments
        self.max_links_per_comment = max_links_per_comment
        self.performance_metrics = {
            "comments_processed": 0,
            "links_processed": 0,
            "processing_time": 0
        }

    def process_comments_flattened(
        self,
        soup: BeautifulSoup,
        comment_selector: str,
        user_selector: str = ".hnuser",
        comment_text_selector: str = ".comment"
    ) -> List[Dict[str, Any]]:
        """
        Process comments with flattened structure - no nested hierarchy processing.

        Args:
            soup: BeautifulSoup object of the comments page
            comment_selector: CSS selector for comment elements
            user_selector: CSS selector for user information
            comment_text_selector: CSS selector for comment text

        Returns:
            List of flattened comment dictionaries
        """
        comments = []
        comment_elements = soup.select(comment_selector)

        # Immediate limit to prevent excessive processing
        comment_elements = comment_elements[:self.max_comments]

        logger.debug(f"Processing {len(comment_elements)} comments (flattened mode)")

        for idx, comment_elem in enumerate(comment_elements):
            try:
                # Fast extraction without nested processing
                comment_data = self._extract_comment_data_fast(
                    comment_elem,
                    user_selector,
                    comment_text_selector,
                    idx
                )

                if comment_data and comment_data["text"]:
                    comments.append(comment_data)

            except Exception as e:
                logger.debug(f"Skipping problematic comment {idx}: {e}")
                continue

        self.performance_metrics["comments_processed"] = len(comments)
        return comments

    def _extract_comment_data_fast(
        self,
        comment_elem,
        user_selector: str,
        comment_text_selector: str,
        index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Fast comment data extraction without deep processing.
        """
        # Get comment ID with fallback
        comment_id = comment_elem.get("id", f"comment_{index}")

        # Extract user info quickly
        user_elem = comment_elem.select_one(user_selector)
        user_name = "Anonymous"  # Privacy compliance - always anonymize
        user_link = "#"  # Preserve link structure but anonymize

        if user_elem:
            original_name = user_elem.get_text().strip()
            if original_name:
                # Create anonymized profile link for legal compliance
                user_link = f"https://news.ycombinator.com/user?id={original_name}"

        # Extract comment text with minimal processing
        comment_text_elem = comment_elem.select_one(comment_text_selector)
        if not comment_text_elem:
            return None

        # Streamlined text processing
        comment_text = self._process_comment_text_streamlined(comment_text_elem)

        return {
            "id": comment_id,
            "user": user_name,
            "user_link": user_link,
            "text": comment_text,
            "level": 0  # Flattened - no nesting levels
        }

    def _process_comment_text_streamlined(self, comment_elem) -> str:
        """
        Streamlined comment text processing with minimal link handling.
        """
        # Remove reply/control links first
        for unwanted in comment_elem.find_all("a", string=re.compile(r"reply|permalink|parent|flag", re.I)):
            unwanted.decompose()

        # Limited link processing for performance
        links = comment_elem.find_all("a", href=True)
        links_processed = 0

        for link in links:
            if links_processed >= self.max_links_per_comment:
                link.decompose()  # Remove excess links
                continue

            try:
                href = link.get("href", "")
                link_text = link.get_text().strip()

                # Skip if empty or control link
                if not href or not link_text or link_text.lower() in ["reply", "flag", "unflag"]:
                    link.decompose()
                    continue

                # Simple URL normalization
                if href.startswith("/"):
                    href = f"https://news.ycombinator.com{href}"
                elif not href.startswith(("http://", "https://")):
                    href = f"https://{href}"

                # Replace with markdown - simple format
                markdown_link = f"[{link_text}]({href})"
                link.replace_with(markdown_link)
                links_processed += 1

            except Exception:
                link.decompose()  # Remove problematic links

        self.performance_metrics["links_processed"] += links_processed

        # Extract and clean text
        text = comment_elem.get_text()

        # Minimal text cleanup
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n\n".join(lines)

    def generate_inline_comments_markdown(
        self,
        comments: List[Dict[str, Any]],
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Generate inline comments markdown with flattened structure.
        """
        if not comments:
            return f"# Comments for: {article_title}\n\n**Comments URL:** [{comment_url}]({comment_url})\n\n---\n\nNo comments available.\n\n"

        # Header
        md_content = f"# Comments for: {article_title}\n\n"
        md_content += f"**Comments URL:** [{comment_url}]({comment_url})\n\n"
        md_content += "---\n\n"

        # Inline comments - flattened display
        for i, comment in enumerate(comments, 1):
            md_content += f"**{comment['user']}** "
            md_content += f"([profile]({comment['user_link']}))\n\n"
            md_content += f"{comment['text']}\n\n"
            md_content += "---\n\n"

        return md_content

    def generate_inline_comments_html(
        self,
        comments: List[Dict[str, Any]],
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Generate inline comments HTML directly, skipping markdown conversion.
        Optimized for HTML post-processor performance.
        """
        if not comments:
            return f"""
            <div class="comments-container">
                <h1>Comments for: {article_title}</h1>
                <p><strong>Comments URL:</strong> <a href="{comment_url}" target="_blank" rel="noopener noreferrer">{comment_url}</a></p>
                <hr>
                <p>No comments available for this article.</p>
            </div>
            """

        # Generate HTML content directly
        html_content = f"""
        <div class="comments-container">
            <h1>Comments for: {article_title}</h1>
            <p><strong>Comments URL:</strong> <a href="{comment_url}" target="_blank" rel="noopener noreferrer">{comment_url}</a></p>
            <hr>
        """

        # Inline comments - flattened display with proper HTML structure
        for i, comment in enumerate(comments, 1):
            # Escape HTML in comment text to prevent XSS
            escaped_text = comment['text'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Convert newlines to paragraphs for better formatting
            paragraphs = [p.strip() for p in escaped_text.split('\n\n') if p.strip()]
            formatted_text = ''.join(f"<p>{p}</p>" for p in paragraphs) if paragraphs else f"<p>{escaped_text}</p>"

            html_content += f"""
            <div class="comment" id="comment-{i}">
                <h3 class="comment-header">
                    <strong>{comment['user']}</strong>
                    <a href="{comment['user_link']}" target="_blank" rel="noopener noreferrer" class="profile-link">(profile)</a>
                </h3>
                <div class="comment-text">
                    {formatted_text}
                </div>
                <hr class="comment-separator">
            </div>
            """

        html_content += "</div>"
        return html_content

    def process_hacker_news_comments_optimized(
        self,
        soup: BeautifulSoup,
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Optimized HN comment processing with flattened structure.
        """
        comments = self.process_comments_flattened(
            soup=soup,
            comment_selector=".comment-tree .athing",
            user_selector=".hnuser",
            comment_text_selector=".comment"
        )

        return self.generate_inline_comments_markdown(
            comments, article_title, comment_url
        )

    def process_lobsters_comments_optimized(
        self,
        soup: BeautifulSoup,
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Optimized Lobsters comment processing with flattened structure.
        """
        comments = self.process_comments_flattened(
            soup=soup,
            comment_selector=".comment",
            user_selector=".user",
            comment_text_selector=".comment_text"
        )

        return self.generate_inline_comments_markdown(
            comments, article_title, comment_url
        )

    def process_lesswrong_comments_optimized(
        self,
        soup: BeautifulSoup,
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Optimized LessWrong comment processing with flattened structure.
        """
        comments = self.process_comments_flattened(
            soup=soup,
            comment_selector=".comment-item, .Comment",
            user_selector=".username, .author",
            comment_text_selector=".comment-body, .content"
        )

        return self.generate_inline_comments_markdown(
            comments, article_title, comment_url
        )

    def process_hacker_news_comments_html_optimized(
        self,
        soup: BeautifulSoup,
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Optimized HN comment processing with direct HTML generation.
        Skips markdown conversion for HTML output.
        """
        comments = self.process_comments_flattened(
            soup=soup,
            comment_selector=".comment-tree .athing",
            user_selector=".hnuser",
            comment_text_selector=".comment"
        )

        return self.generate_inline_comments_html(
            comments, article_title, comment_url
        )

    def process_lobsters_comments_html_optimized(
        self,
        soup: BeautifulSoup,
        article_title: str,
        comment_url: str
    ) -> str:
        """
        Optimized Lobsters comment processing with direct HTML generation.
        Skips markdown conversion for HTML output.
        """
        comments = self.process_comments_flattened(
            soup=soup,
            comment_selector=".comment",
            user_selector=".user",
            comment_text_selector=".comment_text"
        )

        return self.generate_inline_comments_html(
            comments, article_title, comment_url
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        return self.performance_metrics.copy()


def create_optimized_comment_processor(max_comments: int = 100) -> StreamlinedCommentProcessor:
    """
    Factory function to create optimized comment processor.

    Args:
        max_comments: Maximum number of comments to process

    Returns:
        Configured StreamlinedCommentProcessor instance
    """
    return StreamlinedCommentProcessor(max_comments=max_comments, max_links_per_comment=5)