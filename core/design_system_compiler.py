"""
Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from core.logging_config import get_logger


class DesignSystemCompiler:
    """
    Compiles design system CSS custom properties into hardcoded values.

    This compiler processes the design-system.css file and replaces CSS custom
    properties with their computed values for better performance and compatibility
    in self-contained HTML files.
    """

    def __init__(self, themes_dir: Optional[Path] = None):
        """
        Initialize the design system compiler.

        Args:
            themes_dir: Path to themes directory. If None, auto-detects.
        """
        self.logger = get_logger(__name__)
        self.themes_dir = themes_dir or Path(__file__).parent.parent / "themes"
        self.design_system_path = self.themes_dir / "design-system.css"

        # Cache for computed values
        self._computed_values: Optional[Dict[str, str]] = None
        self._compiled_css: Optional[str] = None

    def _extract_css_variables(self, css_content: str) -> Dict[str, str]:
        """
        Extract CSS custom properties and their values from CSS content.

        Args:
            css_content: CSS content to parse

        Returns:
            Dictionary mapping variable names to their values
        """
        variables = {}

        # Match CSS custom properties: --variable-name: value;
        pattern = r'--([a-zA-Z0-9-]+):\s*([^;]+);'
        matches = re.findall(pattern, css_content)

        for var_name, value in matches:
            # Clean up the value (remove comments and whitespace)
            clean_value = re.sub(r'/\*.*?\*/', '', value).strip()
            variables[var_name] = clean_value

        return variables

    def _resolve_variable_references(self, variables: Dict[str, str]) -> Dict[str, str]:
        """
        Resolve CSS custom property references within values.

        Args:
            variables: Dictionary of CSS variables

        Returns:
            Dictionary with resolved variable references
        """
        resolved = variables.copy()
        max_iterations = 10  # Prevent infinite loops

        for _ in range(max_iterations):
            changed = False

            for var_name, value in resolved.items():
                # Find var() references in the value
                var_refs = re.findall(r'var\(--([a-zA-Z0-9-]+)\)', value)

                for ref_var in var_refs:
                    if ref_var in resolved:
                        # Replace the var() reference with the actual value
                        old_value = value
                        value = value.replace(f'var(--{ref_var})', resolved[ref_var])
                        if value != old_value:
                            changed = True
                            resolved[var_name] = value

            if not changed:
                break

        return resolved

    def _add_pixel_reference(self, value: str, base_font_size: int = 16) -> Tuple[str, Optional[str]]:
        """
        Add pixel reference as comment for rem values while preserving original units.

        Args:
            value: CSS value that might contain rem units
            base_font_size: Base font size in pixels (default: 16px)

        Returns:
            Tuple of (original_value, pixel_reference_comment)
        """
        # Match rem values: 1.5rem, 2.618rem, etc.
        rem_matches = re.findall(r'([\d.]+)rem', value)

        if not rem_matches:
            return value, None

        # Calculate pixel equivalents for reference
        px_refs = []
        for rem_str in rem_matches:
            rem_value = float(rem_str)
            px_value = rem_value * base_font_size
            if px_value == int(px_value):
                px_refs.append(f"{int(px_value)}px")
            else:
                px_refs.append(f"{px_value:.2f}px")

        # Create reference comment
        if len(px_refs) == 1:
            comment = f"/* {px_refs[0]} at 16px base */"
        else:
            comment = f"/* {', '.join(px_refs)} at 16px base */"

        return value, comment

    def _compute_hardcoded_values(self) -> Dict[str, str]:
        """
        Compute hardcoded values from design system.
        All variables (typography, spacing, colors) are now in design-system.css.

        Returns:
            Dictionary mapping CSS properties to their hardcoded values
        """
        if not self.design_system_path.exists():
            self.logger.warning(f"Design system file not found: {self.design_system_path}")
            return {}

        try:
            with open(self.design_system_path, 'r', encoding='utf-8') as f:
                design_css = f.read()

            # Extract all variables from design-system.css
            all_variables = self._extract_css_variables(design_css)
            self.logger.debug(f"Extracted {len(all_variables)} variables from design-system.css")

            if not all_variables:
                self.logger.warning("No CSS variables found in design system")
                return {}

            # Resolve any nested variable references
            resolved_variables = self._resolve_variable_references(all_variables)

            self.logger.debug(f"Computed {len(resolved_variables)} total resolved values")
            return resolved_variables

        except Exception as e:
            self.logger.error(f"Error reading design system: {e}")
            return {}

    def get_computed_values(self) -> Dict[str, str]:
        """
        Get computed hardcoded values, using cache if available.

        Returns:
            Dictionary mapping CSS variable names to hardcoded values
        """
        if self._computed_values is None:
            self._computed_values = self._compute_hardcoded_values()

        return self._computed_values

    def _generate_compiled_css_section(self, computed_values: Dict[str, str], include_px_references: bool = True) -> str:
        """
        Generate the compiled CSS section with resolved values.

        Args:
            computed_values: Dictionary of computed resolved values
            include_px_references: Add pixel reference comments for rem values

        Returns:
            CSS string with resolved values
        """
        if not computed_values:
            return "/* No design system values to compile */"

        css_lines = [
            "/* COMPILED DESIGN SYSTEM VALUES */",
            "/* Auto-generated resolved values with var() references expanded */",
            "/* Rem units preserved for accessibility and responsive scaling */",
            "",
            ":root {",
        ]

        # Group variables by category for better organization
        categories = {
            'typography': ['text-', 'font-size-', 'mobile-text-'],
            'spacing': ['space-', 'padding-', 'margin-', 'content-', 'header-', 'component-'],
            'font-weights': ['font-weight-', 'weight-'],
            'line-heights': ['line-height-'],
            'layout': ['measure-', 'width-', 'breakpoint-']
        }

        for category, prefixes in categories.items():
            category_vars = []
            for var_name, value in computed_values.items():
                if any(var_name.startswith(prefix) for prefix in prefixes):
                    category_vars.append((var_name, value))

            if category_vars:
                css_lines.append(f"  /* {category.title()} */")
                for var_name, value in sorted(category_vars):
                    # Add pixel reference comment if value contains rem
                    if include_px_references:
                        _, px_comment = self._add_pixel_reference(value)
                        if px_comment:
                            css_lines.append(f"  --{var_name}: {value}; {px_comment}")
                        else:
                            css_lines.append(f"  --{var_name}: {value};")
                    else:
                        css_lines.append(f"  --{var_name}: {value};")
                css_lines.append("")

        # Add any remaining variables not categorized
        remaining_vars = []
        for var_name, value in computed_values.items():
            categorized = False
            for prefixes in categories.values():
                if any(var_name.startswith(prefix) for prefix in prefixes):
                    categorized = True
                    break
            if not categorized:
                remaining_vars.append((var_name, value))

        if remaining_vars:
            css_lines.append("  /* Other */")
            for var_name, value in sorted(remaining_vars):
                if include_px_references:
                    _, px_comment = self._add_pixel_reference(value)
                    if px_comment:
                        css_lines.append(f"  --{var_name}: {value}; {px_comment}")
                    else:
                        css_lines.append(f"  --{var_name}: {value};")
                else:
                    css_lines.append(f"  --{var_name}: {value};")

        css_lines.append("}")

        return "\n".join(css_lines)

    def compile_design_system(self, target_css: str) -> str:
        """
        Compile the design system by replacing the compilation target section
        with hardcoded values.

        Args:
            target_css: CSS content containing compilation target markers

        Returns:
            CSS content with compiled hardcoded values
        """
        computed_values = self.get_computed_values()

        if not computed_values:
            self.logger.warning("No computed values available for compilation")
            return target_css

        # Generate the compiled CSS section
        compiled_section = self._generate_compiled_css_section(computed_values)

        # Replace the compilation target section
        start_marker = "/* COMPILATION_TARGET_START */"
        end_marker = "/* COMPILATION_TARGET_END */"

        if start_marker in target_css and end_marker in target_css:
            # Replace everything between the markers
            pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
            replacement = f"{start_marker}\n{compiled_section}\n{end_marker}"
            compiled_css = re.sub(pattern, replacement, target_css, flags=re.DOTALL)

            self.logger.debug("Successfully compiled design system values")
            return compiled_css
        else:
            self.logger.warning("Compilation target markers not found in CSS")
            # Append the compiled section to the end
            return target_css + "\n\n" + compiled_section

    def get_compiled_design_system_css(self) -> str:
        """
        Get the fully compiled design system CSS with hardcoded values.

        Returns:
            Compiled CSS content
        """
        if self._compiled_css is None:
            try:
                with open(self.design_system_path, 'r', encoding='utf-8') as f:
                    original_css = f.read()

                self._compiled_css = self.compile_design_system(original_css)

            except Exception as e:
                self.logger.error(f"Error compiling design system CSS: {e}")
                self._compiled_css = "/* Error compiling design system */"

        return self._compiled_css

    def clear_cache(self):
        """Clear the internal caches to force recompilation."""
        self._computed_values = None
        self._compiled_css = None

    def _extract_color_variable_definitions(self) -> str:
        """
        Extract color variable definitions from design-system.css.
        Includes both :root and [data-theme="light"] blocks.

        Returns:
            CSS string with color variable definitions
        """
        if not self.design_system_path.exists():
            return ""

        try:
            with open(self.design_system_path, 'r', encoding='utf-8') as f:
                design_css = f.read()

            # Find the COLOR SYSTEM - DARK THEME section
            color_dark_marker = 'COLOR SYSTEM - DARK THEME'
            color_dark_start = design_css.find(color_dark_marker)
            if color_dark_start != -1:
                # Search FORWARD from the marker for `:root {`
                root_start = design_css.find(':root {', color_dark_start)
                if root_start != -1:
                    # Find the closing brace by counting braces
                    brace_count = 0
                    i = root_start + len(':root {')
                    while i < len(design_css):
                        if design_css[i] == '{':
                            brace_count += 1
                        elif design_css[i] == '}':
                            if brace_count == 0:
                                root_block = design_css[root_start:i+1]
                                break
                            brace_count -= 1
                        i += 1
                    else:
                        root_block = ""
                else:
                    root_block = ""
            else:
                root_block = ""

            # Find the COLOR SYSTEM - LIGHT THEME section
            color_light_marker = 'COLOR SYSTEM - LIGHT THEME'
            color_light_start = design_css.find(color_light_marker)
            if color_light_start != -1:
                # Search FORWARD from the marker for `[data-theme="light"] {`
                light_start = design_css.find('[data-theme="light"] {', color_light_start)
                if light_start != -1:
                    # Find the closing brace by counting braces
                    brace_count = 0
                    i = light_start + len('[data-theme="light"] {')
                    while i < len(design_css):
                        if design_css[i] == '{':
                            brace_count += 1
                        elif design_css[i] == '}':
                            if brace_count == 0:
                                light_block = design_css[light_start:i+1]
                                break
                            brace_count -= 1
                        i += 1
                    else:
                        light_block = ""
                else:
                    light_block = ""
            else:
                light_block = ""

            if root_block and light_block:
                return f"/* COLOR SYSTEM - Injected from design-system.css */\n{root_block}\n\n{light_block}\n"
            elif root_block:
                return f"/* COLOR SYSTEM - Injected from design-system.css */\n{root_block}\n"
            else:
                return ""

        except Exception as e:
            self.logger.error(f"Error extracting color definitions: {e}")
            return ""

    def replace_css_variables(self, css_content: str) -> str:
        """
        Replace design system var() references with hardcoded values.
        Injects color variable definitions for theme switching.
        Removes @import statements since variables are resolved.

        Args:
            css_content: CSS content with var() references

        Returns:
            CSS content with typography/spacing hardcoded, colors injected
        """
        computed_values = self.get_computed_values()

        if not computed_values:
            self.logger.warning("No computed values available for variable replacement")
            return css_content

        # Remove @import statements - no longer needed after compilation
        compiled_css = re.sub(r'@import\s+url\([\'"]?[^\'"]+[\'"]?\);?\s*', '', css_content)

        # Inject color variable definitions at the top
        color_definitions = self._extract_color_variable_definitions()
        if color_definitions:
            compiled_css = color_definitions + "\n" + compiled_css

        # Preserve only COLOR variables for theme switching
        # Everything else (typography, spacing, layout) gets hardcoded
        def is_color_variable(var_name: str) -> bool:
            color_keywords = ['color', 'bg', 'shadow', 'border']
            return any(keyword in var_name for keyword in color_keywords)

        replacements_made = 0
        skipped_colors = 0

        # Replace only non-color variables
        for var_name, value in computed_values.items():
            # Preserve color variables for theme switching
            if is_color_variable(var_name):
                skipped_colors += 1
                continue

            pattern = rf'var\(--{re.escape(var_name)}\)'
            matches = re.findall(pattern, compiled_css)
            if matches:
                compiled_css = re.sub(pattern, value, compiled_css)
                replacements_made += len(matches)

        if replacements_made > 0:
            self.logger.debug(f"Replaced {replacements_made} variable references, preserved {skipped_colors} color variables")
        else:
            self.logger.debug("No variable references found to replace")

        return compiled_css

    def get_design_tokens_for_js(self) -> Dict[str, str]:
        """
        Get design tokens formatted for JavaScript consumption.

        Returns:
            Dictionary of design tokens with camelCase keys
        """
        computed_values = self.get_computed_values()

        # Convert CSS variable names to camelCase for JavaScript
        js_tokens = {}
        for var_name, value in computed_values.items():
            # Convert kebab-case to camelCase: text-large -> textLarge
            camel_case = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), var_name)
            js_tokens[camel_case] = value

        return js_tokens