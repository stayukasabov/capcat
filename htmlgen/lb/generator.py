#!/usr/bin/env python3
"""
Lobsters specific HTML generator implementation.

This module implements the source-specific HTML generation logic for Lobsters,
inheriting from BaseHTMLGenerator and providing Lobsters-specific customizations.

Key Features:
- Lobsters-specific comment pattern recognition (markdown format, same as HN)
- Conditional comment display (only show when comments exist)
- Technical breadcrumb navigation style
- Community-driven tech-focused CSS styling
- Tag display support for Lobsters' tagging system
"""

import re
from pathlib import Path
from typing import List

from htmlgen.base.base_generator import BaseHTMLGenerator, HTMLGeneratorFactory


class LobstersGenerator(BaseHTMLGenerator):
    """
    Lobsters specific HTML generator.

    Implements Lobsters-specific behavior:
    - Comment pattern: **username** ([profile](URL)) (same as HN)
    - Conditional comment links (only when comments exist)
    - Technical navigation style with community focus
    - Tag support for Lobsters' categorization system
    """

    def count_comments(self, comments_file: Path) -> int:
        """
        Count Lobsters comments using markdown profile pattern.

        Lobsters comments follow the same pattern as HN in markdown:
        **username** ([profile](https://lobste.rs/u/username))

        Args:
            comments_file: Path to comments markdown file

        Returns:
            Number of Lobsters comments found
        """
        try:
            if not comments_file.exists():
                return 0

            content = comments_file.read_text(encoding='utf-8')
            pattern = self.source_config['comments']['pattern']
            matches = re.findall(pattern, content)

            count = len(matches)
            self.logger.debug(f"Found {count} Lobsters comments in {comments_file}")
            return count

        except Exception as e:
            self.logger.error(f"Error counting Lobsters comments in {comments_file}: {e}")
            return 0

    def should_show_comment_link(self, comment_count: int) -> bool:
        """
        Lobsters only shows comment links when comments exist.

        Args:
            comment_count: Number of comments

        Returns:
            True if comment link should be shown (Lobsters: only when count > 0)
        """
        conditional_display = self.source_config['comments']['conditional_display']
        threshold = self.source_config['comments'].get('count_threshold', 1)

        if conditional_display:
            return comment_count >= threshold

        return True

    def matches_directory_pattern(self, directory_name: str) -> bool:
        """
        Check if directory matches Lobsters patterns.

        Lobsters supports these naming conventions:
        - lobsters (full name)
        - lb_ (short code)
        - Lobsters (capitalized)

        Args:
            directory_name: Directory name to check

        Returns:
            True if directory belongs to Lobsters
        """
        patterns = self.source_config['directory_patterns']
        dir_lower = directory_name.lower()

        for pattern in patterns:
            if pattern.lower() in dir_lower:
                return True

        return False

    def generate_breadcrumb(self, breadcrumb_path: List[str], **kwargs) -> str:
        """
        Generate Lobsters-specific breadcrumb navigation.

        Lobsters uses technical breadcrumb style with community focus:
        - Simplified navigation for comments pages
        - Community-oriented styling
        - Tag-aware navigation when applicable

        Args:
            breadcrumb_path: List of breadcrumb elements
            **kwargs: Additional context

        Returns:
            Lobsters-styled breadcrumb HTML
        """
        html_subfolder = kwargs.get('html_subfolder', False)
        current_file_path = kwargs.get('current_file_path')

        if not breadcrumb_path:
            return ""

        # For Lobsters comments pages, simplify navigation
        is_comments_page = current_file_path and 'comments.html' in current_file_path
        if is_comments_page and len(breadcrumb_path) > 2:
            # Remove news date from comments breadcrumb for cleaner navigation
            filtered_breadcrumb = []
            for item in breadcrumb_path:
                if not item.startswith('news '):
                    filtered_breadcrumb.append(item)
            breadcrumb_path = filtered_breadcrumb

        # Hide breadcrumb if it's just a single item
        if len(breadcrumb_path) == 1:
            return ""

        breadcrumb_items = []

        for i, item in enumerate(breadcrumb_path):
            if i == len(breadcrumb_path) - 1:
                # Current page - no link, community styling
                breadcrumb_items.append(f"<span class='current-page community'>{self.clean_title_for_display(item)}</span>")
            else:
                # Generate proper link based on position and context
                href = self._generate_breadcrumb_link(breadcrumb_path, i, html_subfolder, is_comments_page)
                cleaned_title = self.clean_title_for_display(item)
                breadcrumb_items.append(f'<a href="{href}" class="community-link" title="Navigate to {cleaned_title}">{cleaned_title}</a>')

        return " / ".join(breadcrumb_items)  # Community-style separator

    def _generate_breadcrumb_link(self, breadcrumb_path: List[str], index: int,
                                html_subfolder: bool, is_comments_page: bool) -> str:
        """
        Generate appropriate breadcrumb link for Lobsters navigation.

        Args:
            breadcrumb_path: Full breadcrumb path
            index: Current item index
            html_subfolder: Whether HTML is in subfolder
            is_comments_page: Whether current page is comments

        Returns:
            Appropriate href for the breadcrumb item
        """
        item = breadcrumb_path[index]
        levels_up = len(breadcrumb_path) - index - 1

        if index == 0:
            # First item handling
            if item.startswith('news '):
                # News date folder - link to index.html
                if html_subfolder:
                    href = "../" * (levels_up + 1) + "index.html"
                else:
                    href = "../" * levels_up + "index.html"
            else:
                # Source folder - link to news.html
                if html_subfolder:
                    href = "../../news.html"
                else:
                    href = "news.html"

        elif index == 1:
            # Second item handling - usually article title
            if len(breadcrumb_path) == 3 and is_comments_page:
                # For comments pages: source -> article -> comments
                href = "article.html"
            elif len(breadcrumb_path) >= 3:
                # For article pages with multiple levels
                if html_subfolder:
                    href = "article.html"
                else:
                    href = "html/article.html"
            else:
                # Fallback
                filename = "index.html" if item.startswith('news ') else "news.html"
                if html_subfolder:
                    href = "../" * (levels_up + 1) + filename
                else:
                    href = "../" * levels_up + filename

        else:
            # Other cases
            filename = "index.html" if item.startswith('news ') else "news.html"
            if html_subfolder:
                href = "../" * (levels_up + 1) + filename
            else:
                href = "../" * levels_up + filename

        return href

    def extract_lobsters_tags(self, content: str) -> List[str]:
        """
        Extract Lobsters-specific tags from content.

        Lobsters uses a tagging system for categorizing stories.
        This method attempts to identify and extract relevant tags.

        Args:
            content: Article content to analyze

        Returns:
            List of identified tags
        """
        tags = []

        # Common Lobsters tags patterns
        tech_keywords = [
            'programming', 'software', 'development', 'code', 'git',
            'linux', 'unix', 'security', 'crypto', 'networking',
            'web', 'mobile', 'databases', 'devops', 'open source'
        ]

        content_lower = content.lower()
        for keyword in tech_keywords:
            if keyword in content_lower:
                tags.append(keyword.replace(' ', '-'))

        # Limit to most relevant tags
        return tags[:5]

    def clean_lobsters_content(self, content: str) -> str:
        """
        Enhanced content cleaning for Lobsters-specific elements.

        Args:
            content: Raw content to clean

        Returns:
            Cleaned content suitable for archival display
        """
        # Apply base cleaning first
        content = self.clean_markdown_content(content)

        # Remove Lobsters-specific UI elements
        # Remove submission metadata
        content = re.sub(r'submitted\s+by\s+\w+', '', content, flags=re.IGNORECASE)

        # Remove tag indicators that appear as text
        content = re.sub(r'\[tags?\]', '', content, flags=re.IGNORECASE)

        # Clean up voting and scoring elements
        content = re.sub(r'\d+\s*points?', '', content, flags=re.IGNORECASE)

        # Remove time indicators
        content = re.sub(r'\d+\s*(hours?|days?|minutes?)\s*ago', '', content, flags=re.IGNORECASE)

        # Clean up multiple spaces and empty lines
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content.strip()

    def generate_article_page(self, markdown_path: str, article_title: str,
                            breadcrumb_path: List[str], html_subfolder: bool = False) -> str:
        """
        Generate Lobsters-style article page with community features.

        Args:
            markdown_path: Path to article markdown
            article_title: Article title
            breadcrumb_path: Breadcrumb path
            html_subfolder: Whether HTML is in subfolder

        Returns:
            Generated HTML for Lobsters article page
        """
        try:
            # Read and process markdown
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Apply Lobsters-specific content cleaning
            markdown_content = self.clean_lobsters_content(markdown_content)

            # Extract tags for this article
            article_tags = self.extract_lobsters_tags(markdown_content)

            # Convert to HTML
            html_content = self.markdown_processor.convert(markdown_content)

            # Apply Lobsters-specific transformations
            html_content = self.remove_grey_placeholder_images(html_content)
            html_content = self.remove_headerlink_anchors(html_content)
            html_content = self.remove_duplicate_h1_title(html_content, article_title)
            html_content = self.wrap_source_url_in_div(html_content)

            if html_subfolder:
                html_content = self.adjust_paths_for_subfolder(html_content)

            # Generate Lobsters-specific breadcrumb
            breadcrumb_html = self.generate_breadcrumb(breadcrumb_path,
                                                     html_subfolder=html_subfolder,
                                                     current_file_path="article.html")

            # Generate Lobsters-specific navigation
            navigation = self._generate_lobsters_navigation(markdown_path, html_subfolder)

            # Load and render template
            template = self._load_template('article.html')
            context = self._get_template_context(
                page_title=f"Capcat - {article_title}",
                article_title=article_title,
                breadcrumb=breadcrumb_html,
                article_content=html_content,
                navigation=navigation,
                article_tags=article_tags  # Add tags to context
            )

            return template.render(**context)

        except Exception as e:
            self.logger.error(f"Error generating Lobsters article page for {markdown_path}: {e}")
            return self.generate_error_page(f"Error loading article: {e}")

    def _generate_lobsters_navigation(self, current_path: str, html_subfolder: bool) -> dict:
        """
        Generate Lobsters-specific navigation with community features.

        Args:
            current_path: Current file path
            html_subfolder: Whether in HTML subfolder

        Returns:
            Navigation context dictionary
        """
        # Generate index navigation
        index_nav = self._generate_index_navigation(current_path, html_subfolder)

        # Generate comments navigation with Lobsters conditional logic
        comments_nav = self._generate_comments_navigation(current_path, html_subfolder)

        return {
            'top': f'<div class="navigation-container community"><div class="index-nav">{index_nav}</div><div class="comments-nav">{comments_nav}</div></div>',
            'bottom': f'<div class="navigation-container community"><div class="index-nav">{index_nav}</div><div class="comments-nav">{comments_nav}</div></div>'
        }

    def _generate_index_navigation(self, current_path: str, html_subfolder: bool) -> str:
        """Generate back to news navigation for Lobsters."""
        back_text = self.source_config['navigation']['back_to_news_text']
        return f'<a href="../news.html" class="index-link community" title="Go to {back_text}"><span>{back_text}</span></a>'

    def _generate_comments_navigation(self, current_path: str, html_subfolder: bool) -> str:
        """Generate comments navigation for Lobsters with conditional display."""
        article_path = Path(current_path)
        article_dir = article_path.parent
        comments_path = article_dir / "comments.md"

        if not comments_path.exists():
            return ""

        # Check comment count for conditional display
        comment_count = self.count_comments(comments_path)
        if not self.should_show_comment_link(comment_count):
            return ""

        # Determine navigation based on current page
        if article_path.name == "comments.md":
            # On comments page - show back to article
            back_text = self.source_config['navigation']['back_to_article_text']
            return f'<a href="article.html" class="article-link community" title="{back_text}"><span>{back_text}</span></a>'
        else:
            # On article page - show view comments
            view_text = self.source_config['navigation']['view_comments_text']
            return f'<a href="comments.html" class="comments-link community" title="{view_text}"><span>{view_text}</span></a>'

    def generate_news_page(self, directory_path: str, title: str, breadcrumb_path: List[str]) -> str:
        """
        Generate Lobsters-style news listing page with community features.

        Args:
            directory_path: Path to directory to list
            title: Page title
            breadcrumb_path: Breadcrumb navigation path

        Returns:
            Generated HTML for Lobsters news page
        """
        try:
            # Generate directory listing with Lobsters-specific styling
            directory_listing = self._generate_lobsters_directory_listing(directory_path)

            # Generate breadcrumb with Lobsters community styling
            breadcrumb_html = self.generate_breadcrumb(breadcrumb_path, current_file_path="news.html")

            # Load and render template
            template = self._load_template('news.html')
            context = self._get_template_context(
                page_title=f"Capcat - {title}",
                breadcrumb=breadcrumb_html,
                directory_listing=directory_listing,
                navigation={'top': '', 'bottom': ''}
            )

            return template.render(**context)

        except Exception as e:
            self.logger.error(f"Error generating Lobsters news page for {directory_path}: {e}")
            return self.generate_error_page(f"Error loading directory: {e}")

    def _generate_lobsters_directory_listing(self, directory_path: str) -> str:
        """
        Generate Lobsters-specific directory listing with community-focused presentation.

        Args:
            directory_path: Path to directory

        Returns:
            HTML directory listing with Lobsters community styling
        """
        # Implementation would be similar to current _generate_directory_listing
        # but with Lobsters-specific comment handling and community-focused styling
        # including tag display support

        # This is a placeholder - in full implementation, this would contain
        # the directory scanning logic with Lobsters-specific features

        return "<p>Lobsters directory listing - to be implemented</p>"


# Register the Lobsters generator with the factory
HTMLGeneratorFactory.register_generator('lb', LobstersGenerator)