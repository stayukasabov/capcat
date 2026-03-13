#!/usr/bin/env python3
"""
LessWrong specific HTML generator implementation.

This module implements the source-specific HTML generation logic for LessWrong,
inheriting from BaseHTMLGenerator and providing LessWrong-specific customizations.

Key Features:
- LessWrong-specific comment pattern recognition (HTML format)
- Conditional comment display (only show when comments exist)
- Academic breadcrumb navigation style
- AI/rationality-focused CSS styling
- Enhanced content cleaning for LessWrong UI elements
"""

import re
from pathlib import Path
from typing import List

from htmlgen.base.base_generator import BaseHTMLGenerator, HTMLGeneratorFactory


class LessWrongGenerator(BaseHTMLGenerator):
    """
    LessWrong specific HTML generator.

    Implements LessWrong-specific behavior:
    - Comment pattern: **username** (<a href="...">profile</a>)
    - Conditional comment links (only when comments exist)
    - Academic navigation style for rationality content
    - AI/rationality-focused styling
    - Enhanced content cleaning
    """

    def count_comments(self, comments_file: Path) -> int:
        """
        Count LessWrong comments using HTML profile pattern.

        LessWrong comments follow this pattern in HTML:
        **username** (<a href="https://www.lesswrong.com/users/username">profile</a>)

        Args:
            comments_file: Path to comments markdown file

        Returns:
            Number of LessWrong comments found
        """
        try:
            if not comments_file.exists():
                return 0

            content = comments_file.read_text(encoding='utf-8')
            pattern = self.source_config['comments']['pattern']
            matches = re.findall(pattern, content)

            count = len(matches)
            self.logger.debug(f"Found {count} LessWrong comments in {comments_file}")
            return count

        except Exception as e:
            self.logger.error(f"Error counting LessWrong comments in {comments_file}: {e}")
            return 0

    def should_show_comment_link(self, comment_count: int) -> bool:
        """
        LessWrong only shows comment links when comments exist.

        Args:
            comment_count: Number of comments

        Returns:
            True if comment link should be shown (LessWrong: only when count > 0)
        """
        conditional_display = self.source_config['comments']['conditional_display']
        threshold = self.source_config['comments'].get('count_threshold', 1)

        if conditional_display:
            return comment_count >= threshold

        return True

    def matches_directory_pattern(self, directory_name: str) -> bool:
        """
        Check if directory matches LessWrong patterns.

        LessWrong supports these naming conventions:
        - lesswrong (lowercase)
        - LessWrong (camelCase)

        Args:
            directory_name: Directory name to check

        Returns:
            True if directory belongs to LessWrong
        """
        patterns = self.source_config['directory_patterns']
        dir_lower = directory_name.lower()

        for pattern in patterns:
            if pattern.lower() in dir_lower:
                return True

        return False

    def generate_breadcrumb(self, breadcrumb_path: List[str], **kwargs) -> str:
        """
        Generate LessWrong-specific breadcrumb navigation.

        LessWrong uses academic breadcrumb style with:
        - Simplified navigation for comments pages
        - Academic styling appropriate for rationality content
        - Enhanced readability for long-form content

        Args:
            breadcrumb_path: List of breadcrumb elements
            **kwargs: Additional context

        Returns:
            LessWrong-styled breadcrumb HTML
        """
        html_subfolder = kwargs.get('html_subfolder', False)
        current_file_path = kwargs.get('current_file_path')

        if not breadcrumb_path:
            return ""

        # For LessWrong comments pages, simplify navigation
        is_comments_page = current_file_path and 'comments.html' in current_file_path
        if is_comments_page and len(breadcrumb_path) > 2:
            # Remove news date from comments breadcrumb for cleaner academic navigation
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
                # Current page - no link, academic styling
                breadcrumb_items.append(f"<span class='current-page academic'>{self.clean_title_for_display(item)}</span>")
            else:
                # Generate proper link based on position and context
                href = self._generate_breadcrumb_link(breadcrumb_path, i, html_subfolder, is_comments_page)
                cleaned_title = self.clean_title_for_display(item)
                breadcrumb_items.append(f'<a href="{href}" class="academic-link" title="Navigate to {cleaned_title}">{cleaned_title}</a>')

        return " › ".join(breadcrumb_items)  # Academic-style separator

    def _generate_breadcrumb_link(self, breadcrumb_path: List[str], index: int,
                                html_subfolder: bool, is_comments_page: bool) -> str:
        """
        Generate appropriate breadcrumb link for LessWrong academic navigation.

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

    def clean_lesswrong_content(self, content: str) -> str:
        """
        Enhanced content cleaning for LessWrong-specific UI elements.

        LessWrong articles often contain UI elements that need cleaning:
        - User interaction elements (voting, timestamps)
        - Navigation elements
        - Site-specific formatting

        Args:
            content: Raw content to clean

        Returns:
            Cleaned content suitable for archival display
        """
        # Apply base cleaning first
        content = self.clean_markdown_content(content)

        # Remove LessWrong-specific UI elements
        # Remove usernames and timestamps pattern: [-]UsernameXhYY
        content = re.sub(r'\[-\]\s*.*?\d+h\d+', '', content)

        # Remove standalone timestamps like "14h20", "14h21"
        content = re.sub(r'\d+h\d+', '', content)

        # Remove "Reply" at the end of comments
        content = re.sub(r'Reply\s*,?\s*', '', content, flags=re.MULTILINE)

        # Remove voting indicators and karma scores
        content = re.sub(r'\d+\s*karma', '', content, flags=re.IGNORECASE)

        # Remove specific usernames that appear as UI artifacts
        content = re.sub(r'\bRobertM\b', '', content)
        content = re.sub(r'\bBrendan Long\b', '', content)

        # Clean up multiple spaces and empty lines
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content.strip()

    def generate_article_page(self, markdown_path: str, article_title: str,
                            breadcrumb_path: List[str], html_subfolder: bool = False) -> str:
        """
        Generate LessWrong-style article page with academic formatting.

        Args:
            markdown_path: Path to article markdown
            article_title: Article title
            breadcrumb_path: Breadcrumb path
            html_subfolder: Whether HTML is in subfolder

        Returns:
            Generated HTML for LessWrong article page
        """
        try:
            # Read and process markdown
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Apply LessWrong-specific content cleaning
            markdown_content = self.clean_lesswrong_content(markdown_content)

            # Convert to HTML
            html_content = self.markdown_processor.convert(markdown_content)

            # Apply LessWrong-specific transformations
            html_content = self.remove_grey_placeholder_images(html_content)
            html_content = self.remove_headerlink_anchors(html_content)
            html_content = self.remove_duplicate_h1_title(html_content, article_title)
            html_content = self.wrap_source_url_in_div(html_content)

            if html_subfolder:
                html_content = self.adjust_paths_for_subfolder(html_content)

            # Generate LessWrong-specific breadcrumb
            breadcrumb_html = self.generate_breadcrumb(breadcrumb_path,
                                                     html_subfolder=html_subfolder,
                                                     current_file_path="article.html")

            # Generate LessWrong-specific navigation
            navigation = self._generate_lesswrong_navigation(markdown_path, html_subfolder)

            # Load and render template
            template = self._load_template('article.html')
            context = self._get_template_context(
                page_title=f"Capcat - {article_title}",
                article_title=article_title,
                breadcrumb=breadcrumb_html,
                article_content=html_content,
                navigation=navigation
            )

            return template.render(**context)

        except Exception as e:
            self.logger.error(f"Error generating LessWrong article page for {markdown_path}: {e}")
            return self.generate_error_page(f"Error loading article: {e}")

    def _generate_lesswrong_navigation(self, current_path: str, html_subfolder: bool) -> dict:
        """
        Generate LessWrong-specific navigation with academic styling.

        Args:
            current_path: Current file path
            html_subfolder: Whether in HTML subfolder

        Returns:
            Navigation context dictionary
        """
        # Generate index navigation
        index_nav = self._generate_index_navigation(current_path, html_subfolder)

        # Generate comments navigation with LessWrong conditional logic
        comments_nav = self._generate_comments_navigation(current_path, html_subfolder)

        return {
            'top': f'<div class="navigation-container academic"><div class="index-nav">{index_nav}</div><div class="comments-nav">{comments_nav}</div></div>',
            'bottom': f'<div class="navigation-container academic"><div class="index-nav">{index_nav}</div><div class="comments-nav">{comments_nav}</div></div>'
        }

    def _generate_index_navigation(self, current_path: str, html_subfolder: bool) -> str:
        """Generate back to news navigation for LessWrong with academic styling."""
        back_text = self.source_config['navigation']['back_to_news_text']
        return f'<a href="../news.html" class="index-link academic" title="Go to {back_text}"><span>{back_text}</span></a>'

    def _generate_comments_navigation(self, current_path: str, html_subfolder: bool) -> str:
        """Generate comments navigation for LessWrong with conditional display."""
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
            return f'<a href="article.html" class="article-link academic" title="{back_text}"><span>{back_text}</span></a>'
        else:
            # On article page - show view comments
            view_text = self.source_config['navigation']['view_comments_text']
            return f'<a href="comments.html" class="comments-link academic" title="{view_text}"><span>{view_text}</span></a>'

    def generate_comments_page(self, comments_path: str, article_title: str,
                             breadcrumb_path: List[str], html_subfolder: bool = False) -> str:
        """
        Generate LessWrong-style comments page with enhanced comment display.

        Args:
            comments_path: Path to comments markdown
            article_title: Article title
            breadcrumb_path: Breadcrumb path
            html_subfolder: Whether HTML is in subfolder

        Returns:
            Generated HTML for LessWrong comments page
        """
        try:
            # Read and process comments
            with open(comments_path, 'r', encoding='utf-8') as f:
                comments_content = f.read()

            # Apply LessWrong-specific comment cleaning
            comments_content = self.clean_lesswrong_content(comments_content)

            # Convert to HTML
            html_content = self.markdown_processor.convert(comments_content)

            # Apply transformations
            html_content = self.remove_grey_placeholder_images(html_content)
            html_content = self.wrap_source_url_in_div(html_content)

            if html_subfolder:
                html_content = self.adjust_paths_for_subfolder(html_content)

            # Generate breadcrumb for comments page
            comments_title = f"{article_title} - Comments"
            breadcrumb_html = self.generate_breadcrumb(breadcrumb_path,
                                                     html_subfolder=html_subfolder,
                                                     current_file_path="comments.html")

            # Generate navigation
            navigation = self._generate_lesswrong_navigation(comments_path, html_subfolder)

            # Load and render comments template
            template = self._load_template('comments.html')
            context = self._get_template_context(
                page_title=f"Capcat - {comments_title}",
                article_title=comments_title,
                breadcrumb=breadcrumb_html,
                article_content=html_content,
                navigation=navigation,
                no_comments_message=self.source_config['comments']['no_comments_message']
            )

            return template.render(**context)

        except Exception as e:
            self.logger.error(f"Error generating LessWrong comments page for {comments_path}: {e}")
            return self.generate_error_page(f"Error loading comments: {e}")


# Register the LessWrong generator with the factory
HTMLGeneratorFactory.register_generator('lesswrong', LessWrongGenerator)