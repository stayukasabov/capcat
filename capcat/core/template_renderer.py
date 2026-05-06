#!/usr/bin/env python3
"""
Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration.
"""

import re
from pathlib import Path
from typing import Any, Dict

from capcat.core.logging_config import get_logger
from capcat.core.design_system_compiler import DesignSystemCompiler
from capcat.core.config import find_project_root, NoProjectError


class TemplateRenderer:
    """
    Simple template renderer that replaces {{placeholder}} variables.
    Much more reliable than complex logic-based HTML generation.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.app_dir = Path(__file__).parent.parent.absolute()
        self._user_themes_dir = self._resolve_user_themes_dir()
        user_ds = self._user_themes_dir / "design-system.css" if self._user_themes_dir else None
        self.design_system_compiler = (
            DesignSystemCompiler(themes_dir=self._user_themes_dir)
            if user_ds and user_ds.exists()
            else DesignSystemCompiler()
        )

    def _resolve_user_themes_dir(self) -> "Path | None":
        """Return Config/themes/ if it exists in the project root, else None."""
        try:
            project_root = find_project_root()
            user_themes = project_root / "Config" / "themes"
            return user_themes if user_themes.is_dir() else None
        except NoProjectError:
            return None

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        html_output_path: str = None,
        html_subfolder: bool = False,
    ) -> str:
        """
        Render a template with the given context variables.

        Args:
            template_name: Name of template file (e.g., "article-with-comments.html")
            context: Dictionary of variables to substitute in template

        Returns:
            Rendered HTML content
        """
        try:
            # Load template file - ensure .html extension
            if not template_name.endswith(".html"):
                template_name = f"{template_name}.html"

            template_path = self.templates_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")

            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Get embedded assets instead of file paths
            embedded_assets = self._get_embedded_assets()

            # Add default context variables with embedded assets
            default_context = embedded_assets

            # Merge contexts (user context takes precedence)
            full_context = {**default_context, **context}

            # Replace all {{variable}} placeholders
            rendered_content = self._substitute_variables(
                template_content, full_context
            )

            return rendered_content

        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            return self._generate_error_template(
                f"Template rendering failed: {e}"
            )

    def _substitute_variables(
        self, content: str, context: Dict[str, Any]
    ) -> str:
        """
        Replace {{variable}} placeholders with actual values.

        Args:
            content: Template content with {{placeholder}} variables
            context: Dictionary of variable name -> value mappings

        Returns:
            Content with variables substituted
        """

        def replace_variable(match):
            var_name = match.group(1).strip()
            if var_name in context:
                value = context[var_name]
                # Convert to string if needed
                return str(value) if value is not None else ""
            else:
                self.logger.warning(f"Template variable not found: {var_name}")
                return f"{{{{MISSING: {var_name}}}}}"

        # Replace {{variable}} patterns
        pattern = r"\{\{\s*([^}]+)\s*\}\}"
        return re.sub(pattern, replace_variable, content)

    def _get_embedded_assets(self) -> Dict[str, str]:
        """
        Read and embed CSS and JavaScript assets into the template context.

        Returns:
            Dictionary containing embedded styles and scripts
        """
        try:
            # Read base.css - prefer Config/themes/ over package copy
            user_base = self._user_themes_dir / "base.css" if self._user_themes_dir else None
            base_css_path = (
                user_base if user_base and user_base.exists()
                else self.app_dir / "themes" / "base.css"
            )
            base_css_content = ""
            if base_css_path.exists():
                with open(base_css_path, "r", encoding="utf-8") as f:
                    base_css_content = f.read()

            # Compile CSS: replace all var() references with hardcoded values
            # Color variables preserved for theme switching
            combined_css = self.design_system_compiler.replace_css_variables(base_css_content)

            # Read JavaScript
            js_path = self.app_dir / "themes" / "js" / "capcat.js"
            js_content = ""
            if js_path.exists():
                with open(js_path, "r", encoding="utf-8") as f:
                    js_content = f.read()

            # Return embedded assets wrapped in appropriate HTML tags
            return {
                "embedded_styles": f"<style>\n{combined_css}\n</style>",
                "embedded_script": f"<script>\n{js_content}\n</script>",
            }

        except Exception as e:
            self.logger.error(f"Error reading embedded assets: {e}")
            return {
                "embedded_styles": "<!-- Error loading embedded styles -->",
                "embedded_script": "<!-- Error loading embedded script -->",
            }

    def _generate_error_template(self, error_message: str) -> str:
        """Generate minimal error page when template rendering fails."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Template Error</title>
</head>
<body>
    <h1>Template Rendering Error</h1>
    <p>{error_message}</p>
</body>
</html>"""
