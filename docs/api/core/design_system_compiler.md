# core.design_system_compiler

**File:** `Application/core/design_system_compiler.py`

## Description

Design System Compiler for Capcat HTML Generation

Compiles CSS custom properties from the design system into hardcoded values
for performance optimization and self-contained HTML generation.

## Classes

### DesignSystemCompiler

Compiles design system CSS custom properties into hardcoded values.

This compiler processes the design-system.css file and replaces CSS custom
properties with their computed values for better performance and compatibility
in self-contained HTML files.

#### Methods

##### __init__

```python
def __init__(self, themes_dir: Optional[Path] = None)
```

Initialize the design system compiler.

Args:
    themes_dir: Path to themes directory. If None, auto-detects.

**Parameters:**

- `self`
- `themes_dir` (Optional[Path]) *optional*

##### _extract_css_variables

```python
def _extract_css_variables(self, css_content: str) -> Dict[str, str]
```

Extract CSS custom properties and their values from CSS content.

Args:
    css_content: CSS content to parse

Returns:
    Dictionary mapping variable names to their values

**Parameters:**

- `self`
- `css_content` (str)

**Returns:** Dict[str, str]

##### _resolve_variable_references

```python
def _resolve_variable_references(self, variables: Dict[str, str]) -> Dict[str, str]
```

Resolve CSS custom property references within values.

Args:
    variables: Dictionary of CSS variables

Returns:
    Dictionary with resolved variable references

**Parameters:**

- `self`
- `variables` (Dict[str, str])

**Returns:** Dict[str, str]

##### _add_pixel_reference

```python
def _add_pixel_reference(self, value: str, base_font_size: int = 16) -> Tuple[str, Optional[str]]
```

Add pixel reference as comment for rem values while preserving original units.

Args:
    value: CSS value that might contain rem units
    base_font_size: Base font size in pixels (default: 16px)

Returns:
    Tuple of (original_value, pixel_reference_comment)

**Parameters:**

- `self`
- `value` (str)
- `base_font_size` (int) *optional*

**Returns:** Tuple[str, Optional[str]]

##### _compute_hardcoded_values

```python
def _compute_hardcoded_values(self) -> Dict[str, str]
```

Compute hardcoded values from design system.
All variables (typography, spacing, colors) are now in design-system.css.

Returns:
    Dictionary mapping CSS properties to their hardcoded values

**Parameters:**

- `self`

**Returns:** Dict[str, str]

##### get_computed_values

```python
def get_computed_values(self) -> Dict[str, str]
```

Get computed hardcoded values, using cache if available.

Returns:
    Dictionary mapping CSS variable names to hardcoded values

**Parameters:**

- `self`

**Returns:** Dict[str, str]

##### _generate_compiled_css_section

```python
def _generate_compiled_css_section(self, computed_values: Dict[str, str], include_px_references: bool = True) -> str
```

Generate the compiled CSS section with resolved values.

Args:
    computed_values: Dictionary of computed resolved values
    include_px_references: Add pixel reference comments for rem values

Returns:
    CSS string with resolved values

**Parameters:**

- `self`
- `computed_values` (Dict[str, str])
- `include_px_references` (bool) *optional*

**Returns:** str

⚠️ **High complexity:** 17

##### compile_design_system

```python
def compile_design_system(self, target_css: str) -> str
```

Compile the design system by replacing the compilation target section
with hardcoded values.

Args:
    target_css: CSS content containing compilation target markers

Returns:
    CSS content with compiled hardcoded values

**Parameters:**

- `self`
- `target_css` (str)

**Returns:** str

##### get_compiled_design_system_css

```python
def get_compiled_design_system_css(self) -> str
```

Get the fully compiled design system CSS with hardcoded values.

Returns:
    Compiled CSS content

**Parameters:**

- `self`

**Returns:** str

##### clear_cache

```python
def clear_cache(self)
```

Clear the internal caches to force recompilation.

**Parameters:**

- `self`

##### _extract_color_variable_definitions

```python
def _extract_color_variable_definitions(self) -> str
```

Extract color variable definitions from design-system.css.
Includes both :root and [data-theme="light"] blocks.

Returns:
    CSS string with color variable definitions

**Parameters:**

- `self`

**Returns:** str

⚠️ **High complexity:** 18

##### replace_css_variables

```python
def replace_css_variables(self, css_content: str) -> str
```

Replace design system var() references with hardcoded values.
Injects color variable definitions for theme switching.
Removes @import statements since variables are resolved.

Args:
    css_content: CSS content with var() references

Returns:
    CSS content with typography/spacing hardcoded, colors injected

**Parameters:**

- `self`
- `css_content` (str)

**Returns:** str

##### get_design_tokens_for_js

```python
def get_design_tokens_for_js(self) -> Dict[str, str]
```

Get design tokens formatted for JavaScript consumption.

Returns:
    Dictionary of design tokens with camelCase keys

**Parameters:**

- `self`

**Returns:** Dict[str, str]


## Functions

### is_color_variable

```python
def is_color_variable(var_name: str) -> bool
```

**Parameters:**

- `var_name` (str)

**Returns:** bool

