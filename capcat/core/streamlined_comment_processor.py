#!/usr/bin/env python3
"""
Streamlined comment processor for optimizing nested structure handling and reducing conversion time.
Designed to flatten complex comment hierarchies and provide inline comment display.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from bs4 import BeautifulSoup
import logging

from capcat.core.storage_manager import article_md_filename, find_article_md

logger = logging.getLogger(__name__)


class StreamlinedCommentProcessor:
    """
    Comment processor that extracts comments with optional nesting depth preservation.
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
        comment_text_selector: str = ".comment",
        depth_fn: Optional[Callable[[Any], int]] = None,
        comment_permalink_fn: Optional[Callable[[str], str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process comments preserving nesting depth.

        Args:
            soup: BeautifulSoup object of the comments page
            comment_selector: CSS selector for comment elements
            user_selector: CSS selector for user information
            comment_text_selector: CSS selector for comment text
            depth_fn: Optional callable(element) -> int returning nesting depth.
                      If None, all comments get level=0.
            comment_permalink_fn: Optional callable(comment_id: str) -> str that
                      generates a direct comment URL from the comment element's id
                      attribute. No username is passed or stored. If None, user_link
                      falls back to '#'.

        Returns:
            List of comment dicts with 'level' field reflecting nesting depth.
            'user' is always 'Anonymous'. 'user_link' is a comment permalink (no
            username stored anywhere in the output).
        """
        comments = []
        comment_elements = soup.select(comment_selector)
        comment_elements = comment_elements[:self.max_comments]

        logger.debug(f"Processing {len(comment_elements)} comments")

        for idx, comment_elem in enumerate(comment_elements):
            try:
                comment_data = self._extract_comment_data_fast(
                    comment_elem,
                    user_selector,
                    comment_text_selector,
                    idx,
                    depth_fn=depth_fn,
                    comment_permalink_fn=comment_permalink_fn,
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
        index: int,
        depth_fn: Optional[Callable[[Any], int]] = None,
        comment_permalink_fn: Optional[Callable[[str], str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fast comment data extraction without deep processing.
        Username is never read or stored. user_link is derived from the comment
        element's id attribute via comment_permalink_fn so readers can validate
        the comment on the source site without capcat retaining personal data.
        Falls back to '#' when no permalink function is provided.
        """
        comment_id = comment_elem.get("id", "")
        user_link = (
            comment_permalink_fn(comment_id)
            if comment_id and comment_permalink_fn
            else "#"
        )

        comment_text_elem = comment_elem.select_one(comment_text_selector)
        if not comment_text_elem:
            return None

        comment_text = self._process_comment_text_streamlined(comment_text_elem)

        depth = 0
        if depth_fn is not None:
            try:
                depth = int(depth_fn(comment_elem))
            except (ValueError, TypeError):
                depth = 0

        return {
            "id": comment_id,
            "user": "Anonymous",
            "user_link": user_link,
            "text": comment_text,
            "level": depth,
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
        comment_url: str,
        article_folder_path: str = None
    ) -> str:
        """
        Generate inline comments markdown with flattened structure.

        If article_folder_path is provided, prepends and appends a
        ← [[article_stem|Article]] wikilink for Obsidian graph connectivity.
        """
        if not comments:
            return f"# Comments for: {article_title}\n\n**Comments URL:** [{comment_url}]({comment_url})\n\n---\n\nNo comments available.\n\n"

        # Derive article stem for Obsidian wikilink
        if article_folder_path:
            article_md = find_article_md(Path(article_folder_path))
            article_stem = article_md.stem if article_md else article_md_filename(article_title)[:-3]
        else:
            article_stem = article_md_filename(article_title)[:-3]
        wikilink = f"← [[{article_stem}|Article]]"

        # Header
        md_content = f"{wikilink}\n\n"
        md_content += f"# Comments for: {article_title}\n\n"
        md_content += f"**Comments URL:** [{comment_url}]({comment_url})\n\n"
        md_content += "---\n\n"

        # Inline comments - flattened display
        for i, comment in enumerate(comments, 1):
            level = comment.get('level', 0)
            prefix = "> " * level  # e.g. "" / "> " / "> > "

            md_content += f"{prefix}**{comment['user']}**\n\n"

            # Prefix each paragraph of the comment text
            for paragraph in comment['text'].split('\n\n'):
                paragraph = paragraph.strip()
                if paragraph:
                    md_content += f"{prefix}{paragraph}\n\n"

            md_content += f"{prefix}---\n\n"

        md_content += f"\n{wikilink}\n"
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

            level = comment.get('level', 0)
            if level > 0:
                indent_style = f'style="margin-left: {level * 24}px; border-left: 2px solid #e0e0e0; padding-left: 8px;"'
            else:
                indent_style = ''

            html_content += f"""
            <div class="comment" id="comment-{i}" {indent_style}>
                <h3 class="comment-header">
                    <strong>{comment['user']}</strong>
                </h3>
                <div class="comment-text">
                    {formatted_text}
                </div>
                <hr class="comment-separator">
            </div>
            """

        html_content += "</div>"
        return html_content

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