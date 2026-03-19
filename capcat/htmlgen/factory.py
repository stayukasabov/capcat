"""Factory for creating ArticleHTMLGenerator instances."""
from __future__ import annotations
from capcat.htmlgen.generator import ArticleHTMLGenerator


class HTMLGeneratorFactory:
    """Construction point for HTML generators.

    Minimal now. Registry pattern for source-specific subclasses
    added when the first source requires custom HTML logic.
    """

    @staticmethod
    def create() -> ArticleHTMLGenerator:
        """Return a new ArticleHTMLGenerator instance."""
        return ArticleHTMLGenerator()
