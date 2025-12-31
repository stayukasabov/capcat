# core.template_renderer

**File:** `Application/core/template_renderer.py`

## Description

Simple Template Renderer for Capcat
Replaces {{placeholder}} variables with actual values from configuration.

## Classes

### TemplateRenderer

Simple template renderer that replaces {{placeholder}} variables.
Much more reliable than complex logic-based HTML generation.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### render_template

```python
def render_template(self, template_name: str, context: Dict[str, Any], html_output_path: str = None, html_subfolder: bool = False) -> str
```

Render a template with the given context variables.

Args:
    template_name: Name of template file (e.g., "article-with-comments.html")
    context: Dictionary of variables to substitute in template

Returns:
    Rendered HTML content

**Parameters:**

- `self`
- `template_name` (str)
- `context` (Dict[str, Any])
- `html_output_path` (str) *optional*
- `html_subfolder` (bool) *optional*

**Returns:** str

##### _substitute_variables

```python
def _substitute_variables(self, content: str, context: Dict[str, Any]) -> str
```

Replace {{variable}} placeholders with actual values.

Args:
    content: Template content with {{placeholder}} variables
    context: Dictionary of variable name -> value mappings

Returns:
    Content with variables substituted

**Parameters:**

- `self`
- `content` (str)
- `context` (Dict[str, Any])

**Returns:** str

##### _get_embedded_assets

```python
def _get_embedded_assets(self) -> Dict[str, str]
```

Read and embed CSS and JavaScript assets into the template context.

Returns:
    Dictionary containing embedded styles and scripts

**Parameters:**

- `self`

**Returns:** Dict[str, str]

##### _generate_error_template

```python
def _generate_error_template(self, error_message: str) -> str
```

Generate minimal error page when template rendering fails.

**Parameters:**

- `self`
- `error_message` (str)

**Returns:** str


## Functions

### replace_variable

```python
def replace_variable(match)
```

**Parameters:**

- `match`

