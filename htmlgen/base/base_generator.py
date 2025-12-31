#!/usr/bin/env python3
"""
Base HTML Generator for Compartmentalized HTML Generation System.

This module provides the abstract base class and common functionality for all
source-specific HTML generators. It replaces the monolithic html_generator.py
with a modular, configuration-driven approach.

Architecture:
- BaseHTMLGenerator: Abstract base class with common functionality
- Source-specific generators inherit from this base
- Configuration-driven behavior via YAML files
- Template system with override capability
- Factory pattern for generator instantiation
"""

import os
import re
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime

import markdown
from markdown.extensions import codehilite, toc, tables, fenced_code
from pygments.formatters import HtmlFormatter

# Try to use Jinja2 for better templating, fall back to simple string replacement
try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    # Fallback simple template class
    class Template:
        def __init__(self, template_string):
            self.template_string = template_string

        def render(self, **kwargs):
            result = self.template_string
            for key, value in kwargs.items():
                result = result.replace('{{' + key + '}}', str(value))
            return result

from core.logging_config import get_logger
from core.config import get_config


class HTMLGeneratorError(Exception):
    """Base exception for HTML generation errors."""
    pass


class ConfigurationError(HTMLGeneratorError):
    """Raised when configuration validation fails."""
    pass


class TemplateError(HTMLGeneratorError):
    """Raised when template processing fails."""
    pass


class BaseHTMLGenerator(ABC):
    """
    Abstract base class for source-specific HTML generators.

    Provides common functionality and enforces the interface that all
    source-specific generators must implement. This replaces the monolithic
    html_generator.py with a modular, maintainable architecture.

    Key Features:
    - Configuration-driven behavior via YAML files
    - Template system with source-specific overrides
    - Common HTML processing utilities
    - Abstract methods for source-specific logic
    - Comprehensive error handling and logging

    Design Patterns:
    - Template Method: Base methods call abstract methods for customization
    - Strategy: Different comment parsing strategies per source
    - Factory: Dynamic generator instantiation based on source
    - Configuration: YAML-driven behavior modification
    """

    def __init__(self, source_id: str):
        """
        Initialize base HTML generator with source-specific configuration.

        Args:
            source_id: Unique identifier for the source (e.g., 'hn', 'lesswrong')

        Raises:
            ConfigurationError: If source configuration is invalid
            FileNotFoundError: If configuration files are missing
        """
        self.source_id = source_id
        self.logger = get_logger(f"{__name__}.{source_id}")
        self.config = get_config()

        # Load source-specific configuration
        self.source_config = self._load_source_config()

        # Validate configuration against schema
        self._validate_configuration()

        # Initialize markdown processor with source-specific settings
        self.markdown_processor = self._setup_markdown_processor()

        # Cache template objects for performance
        self._template_cache = {}

        self.logger.debug(f"Initialized {self.__class__.__name__} for source '{source_id}'")

    def _load_source_config(self) -> Dict[str, Any]:
        """
        Load source-specific configuration from YAML file.

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ConfigurationError: If required fields are missing
        """
        # Get path to source config file
        config_path = Path(__file__).parent.parent / self.source_id / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config:
                raise ConfigurationError(f"Empty configuration file: {config_path}")

            self.logger.debug(f"Loaded configuration from {config_path}")
            return config

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_path}: {e}")

    def _validate_configuration(self) -> None:
        """
        Validate source configuration against schema.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Required fields that all sources must have
        required_fields = ['source_id', 'display_name', 'comments', 'navigation', 'layout', 'directory_patterns']

        for field in required_fields:
            if field not in self.source_config:
                raise ConfigurationError(f"Missing required field '{field}' in {self.source_id} configuration")

        # Validate source_id matches directory structure
        if self.source_config['source_id'] != self.source_id:
            raise ConfigurationError(f"Configuration source_id '{self.source_config['source_id']}' doesn't match directory '{self.source_id}'")

        # Validate comments configuration
        comments_config = self.source_config['comments']
        if comments_config.get('enabled', True) and not comments_config.get('pattern'):
            raise ConfigurationError(f"Comment pattern required when comments are enabled for {self.source_id}")

        self.logger.debug(f"Configuration validation passed for {self.source_id}")

    def _setup_markdown_processor(self) -> markdown.Markdown:
        """
        Configure markdown processor with source-specific extensions.

        Returns:
            Configured markdown processor instance
        """
        # Base extensions that all sources use
        extensions = [
            'codehilite',
            'toc',
            'tables',
            'fenced_code',
            'attr_list'
        ]

        # Source-specific extensions from configuration
        content_config = self.source_config.get('content', {})
        # Note: pymdownx extensions require additional installation
        # For now, skip math rendering to avoid dependency issues
        # if content_config.get('math_rendering', False):
        #     extensions.append('pymdownx.arithmatex')

        extension_configs = {
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': content_config.get('code_highlighting', True),
                'noclasses': False
            },
            'toc': {
                'permalink': True,
                'permalink_title': 'Link to this section'
            }
        }

        return markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_configs
        )

    def _get_app_directory(self) -> Path:
        """Get absolute path to Application directory for assets."""
        return Path(__file__).parent.parent.parent.absolute()

    def _load_template(self, template_name: str) -> Template:
        """
        Load and cache template with source-specific override support.

        Args:
            template_name: Name of template (e.g., 'article.html', 'comments.html')

        Returns:
            Compiled template object

        Raises:
            TemplateError: If template file is not found or invalid
        """
        # Check cache first
        cache_key = f"{self.source_id}:{template_name}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]

        # Determine template path with override support
        template_path = self._resolve_template_path(template_name)

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Create Template object with {{variable}} syntax
            template = Template(template_content)

            # Cache for performance
            self._template_cache[cache_key] = template

            self.logger.debug(f"Loaded template: {template_path}")
            return template

        except FileNotFoundError:
            raise TemplateError(f"Template not found: {template_path}")
        except Exception as e:
            raise TemplateError(f"Error loading template {template_path}: {e}")

    def _resolve_template_path(self, template_name: str) -> Path:
        """
        Resolve template path with source-specific override support.

        Template resolution order:
        1. Source-specific template (htmlgen/source_id/templates/template_name)
        2. Base template (htmlgen/base/templates/template_name)

        Args:
            template_name: Name of template file

        Returns:
            Path to template file

        Raises:
            TemplateError: If template is not found
        """
        base_dir = Path(__file__).parent.parent

        # Check for source-specific template override
        source_template_path = base_dir / self.source_id / "templates" / template_name
        if source_template_path.exists():
            return source_template_path

        # Fall back to base template
        base_template_path = base_dir / "base" / "templates" / template_name
        if base_template_path.exists():
            return base_template_path

        raise TemplateError(f"Template '{template_name}' not found in source or base templates")

    def _get_template_context(self, **kwargs) -> Dict[str, Any]:
        """
        Build template context with common variables and source-specific data.

        Args:
            **kwargs: Additional context variables

        Returns:
            Complete template context dictionary
        """
        app_dir = self._get_app_directory()

        # Base context available to all templates with relative paths
        # HTML files are generated in News/Source_Date/Article/html/
        # So we need to go up 4 levels to reach Application: ../../../../Application/
        relative_app_path = "../../../../Application"
        context = {
            'app_dir': relative_app_path,
            'source_id': self.source_id,
            'display_name': self.source_config['display_name'],
            'custom_css_classes': self.source_config.get('layout', {}).get('custom_css_classes', []),
            'timestamp': datetime.now().isoformat(),
        }

        # Add source-specific navigation text
        nav_config = self.source_config.get('navigation', {})
        context.update({
            'back_to_news_text': nav_config.get('back_to_news_text', 'Back to News'),
            'view_comments_text': nav_config.get('view_comments_text', 'View Comments'),
            'back_to_article_text': nav_config.get('back_to_article_text', 'Back to Article'),
        })

        # Merge in provided context
        context.update(kwargs)

        return context

    # Abstract methods that source-specific generators must implement

    @abstractmethod
    def count_comments(self, comments_file: Path) -> int:
        """
        Count comments using source-specific pattern.

        Args:
            comments_file: Path to comments markdown file

        Returns:
            Number of comments found
        """
        pass

    @abstractmethod
    def should_show_comment_link(self, comment_count: int) -> bool:
        """
        Determine whether to show comment link based on source-specific rules.

        Args:
            comment_count: Number of comments

        Returns:
            True if comment link should be shown
        """
        pass

    @abstractmethod
    def matches_directory_pattern(self, directory_name: str) -> bool:
        """
        Check if directory name matches this source's patterns.

        Args:
            directory_name: Name of directory to check

        Returns:
            True if directory belongs to this source
        """
        pass

    @abstractmethod
    def generate_breadcrumb(self, breadcrumb_path: List[str], **kwargs) -> str:
        """
        Generate breadcrumb navigation HTML with source-specific logic.

        Args:
            breadcrumb_path: List of breadcrumb elements
            **kwargs: Additional context (html_subfolder, current_file_path, etc.)

        Returns:
            Breadcrumb HTML string
        """
        pass

    # Common utility methods available to all generators

    def clean_markdown_content(self, content: str) -> str:
        """Clean up problematic content in markdown that could interfere with templates."""
        # Remove {{ message }} tags that appear in GitHub and other sites
        content = re.sub(r'\{\{\s*message\s*\}\}', '', content)

        # Remove other common template-like patterns that cause issues
        content = re.sub(r'\{\{\s*[^}]+\s*\}\}', '', content)

        # Clean up any resulting empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content.strip()

    def remove_grey_placeholder_images(self, html_content: str) -> str:
        """Remove grey-placeholder images from HTML content."""
        return re.sub(r'<img[^>]*src="[^"]*grey-placeholder[^"]*"[^>]*/?>', '', html_content)

    def remove_headerlink_anchors(self, html_content: str) -> str:
        """Remove headerlink anchor tags from HTML content."""
        pattern = r'<a\s+class="headerlink"[^>]*>.*?</a>'
        return re.sub(pattern, '', html_content, flags=re.IGNORECASE | re.DOTALL)

    def remove_duplicate_h1_title(self, html_content: str, article_title: str) -> str:
        """Remove duplicate H1 title from article content if it matches header title."""
        clean_title = article_title.strip()

        h1_patterns = [
            rf'<h1[^>]*>\s*{re.escape(clean_title)}\s*</h1>',
            rf'<h1[^>]*>[^<]*{re.escape(clean_title.split("|")[0].strip() if "|" in clean_title else clean_title)}[^<]*</h1>',
            r'^\s*<h1[^>]*>.*?</h1>\s*'
        ]

        for pattern in h1_patterns:
            if re.search(pattern, html_content, flags=re.IGNORECASE | re.DOTALL):
                html_content = re.sub(pattern, '', html_content, count=1, flags=re.IGNORECASE | re.DOTALL)
                break

        return html_content.strip()

    def wrap_source_url_in_div(self, html_content: str) -> str:
        """Transform source/comments URL paragraphs into semantic div elements."""
        pattern = r'(<p[^>]*>)\s*(<strong>(?:Source URL|Comments URL):</strong>\s*<a\s+href="[^"]*"[^>]*>[^<]*</a>)\s*(</p>)'

        def replace_source_url(match):
            p_open, content, p_close = match.groups()
            return f'<div class="source-url">{content}</div>'

        return re.sub(pattern, replace_source_url, html_content, flags=re.IGNORECASE)

    def adjust_paths_for_subfolder(self, html_content: str) -> str:
        """Adjust relative paths in HTML content when HTML files are in html/ subfolder."""
        # Adjust various media paths: folder/ -> ../folder/
        media_folders = ['images', 'files', 'audio', 'video']

        for folder in media_folders:
            # Adjust src attributes
            html_content = re.sub(f'src="{folder}/', f'src="../{folder}/', html_content)
            html_content = re.sub(f"src='{folder}/", f"src='../{folder}/", html_content)

            # Adjust href attributes
            html_content = re.sub(f'href="{folder}/', f'href="../{folder}/', html_content)
            html_content = re.sub(f"href='{folder}/", f"href='../{folder}/", html_content)

        return html_content

    def clean_title_for_display(self, title: str) -> str:
        """Clean title for display by removing underscores, dashes, and formatting."""
        # Remove leading numbers and underscores (e.g., "01_" -> "")
        cleaned = re.sub(r'^\d+_', '', title)

        # Replace underscores with spaces
        cleaned = cleaned.replace('_', ' ')

        # Replace multiple dashes with single space, but keep single dashes as hyphens
        cleaned = re.sub(r'--+', ' ', cleaned)

        # Clean up multiple spaces (but preserve intended spacing in test case)
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def format_date_for_header(self, title: str) -> str:
        """Format dates in titles specifically for h1 headers."""
        months = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }

        # Pattern to match dates in DD-MM-YYYY format
        date_pattern = r'(\d{1,2})-(\d{1,2})-(\d{4})(?=\s*$)'
        match = re.search(date_pattern, title)

        if match:
            day, month, year = match.groups()
            if month in months:
                month_name = months[month]
                formatted_date = f"{day} {month_name} {year}"
                return re.sub(date_pattern, formatted_date, title)

        return title

    def generate_error_page(self, error_message: str) -> str:
        """Generate error page HTML using source template."""
        try:
            template = self._load_template('article.html')
            context = self._get_template_context(
                page_title="Capcat - Error",
                article_title="Error",
                breadcrumb="",
                article_content=f"<div class='error'><h2>Error</h2><p>{error_message}</p></div>",
                navigation={'top': '', 'bottom': ''}
            )
            return template.render(**context)
        except Exception as e:
            # Fallback to basic HTML if template fails
            self.logger.error(f"Error generating error page template: {e}")
            return f"""<!DOCTYPE html>
<html><head><title>Error</title></head>
<body><h1>Error</h1><p>{error_message}</p></body>
</html>"""


class HTMLGeneratorFactory:
    """
    Factory for creating source-specific HTML generators.

    Implements the Factory pattern to dynamically instantiate the correct
    generator based on source identifier. This decouples the main system
    from knowing about specific generator implementations.
    """

    _generators = {}  # Registry of available generators

    @classmethod
    def register_generator(cls, source_id: str, generator_class: type) -> None:
        """
        Register a generator class for a source.

        Args:
            source_id: Unique source identifier
            generator_class: Generator class that inherits from BaseHTMLGenerator
        """
        cls._generators[source_id] = generator_class

    @classmethod
    def create_generator(cls, source_id: str) -> BaseHTMLGenerator:
        """
        Create generator instance for the specified source.

        Args:
            source_id: Source identifier to create generator for

        Returns:
            Source-specific HTML generator instance

        Raises:
            ValueError: If source is not registered
        """
        if source_id not in cls._generators:
            raise ValueError(f"No generator registered for source: {source_id}")

        generator_class = cls._generators[source_id]
        return generator_class(source_id)

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """
        Get list of all registered source identifiers.

        Returns:
            List of available source IDs
        """
        return list(cls._generators.keys())

    @classmethod
    def detect_source_from_directory(cls, directory_name: str) -> Optional[str]:
        """
        Detect source from directory name using all registered generators.

        Args:
            directory_name: Name of directory to identify

        Returns:
            Source ID if match found, None otherwise
        """
        for source_id in cls._generators:
            try:
                generator = cls.create_generator(source_id)
                if generator.matches_directory_pattern(directory_name):
                    return source_id
            except Exception:
                continue  # Skip if generator creation fails

        return None