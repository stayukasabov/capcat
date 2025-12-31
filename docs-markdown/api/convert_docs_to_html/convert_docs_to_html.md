# convert_docs_to_html

**File:** `Application/convert_docs_to_html.py`

## Description

Convert Markdown documentation to clean HTML with minimal styling.
Only applies styling to code blocks, ASCII art, and Mermaid diagrams.

## Constants

### PYGMENTS_AVAILABLE

**Value:** `True`

### PYGMENTS_AVAILABLE

**Value:** `False`

## Functions

### create_basic_html_template

```python
def create_basic_html_template()
```

Create a clean HTML template with minimal styling.

### detect_ascii_art

```python
def detect_ascii_art(content)
```

Detect ASCII art patterns in content.

**Parameters:**

- `content`

### convert_markdown_to_html

```python
def convert_markdown_to_html(markdown_content, title = 'Documentation')
```

Convert markdown content to HTML with minimal styling.

**Parameters:**

- `markdown_content`
- `title` *optional*

⚠️ **High complexity:** 26

### create_navigation

```python
def create_navigation(file_path, base_path)
```

Create navigation breadcrumb for the file.

**Parameters:**

- `file_path`
- `base_path`

### process_file

```python
def process_file(md_file_path, output_dir, docs_base_dir)
```

Process a single markdown file.

**Parameters:**

- `md_file_path`
- `output_dir`
- `docs_base_dir`

### create_directory_index

```python
def create_directory_index(dir_path, title)
```

Create an index.html file for a directory.

**Parameters:**

- `dir_path`
- `title`

⚠️ **High complexity:** 18

### main

```python
def main()
```

Main conversion function.

### extract_code_block

```python
def extract_code_block(match)
```

**Parameters:**

- `match`

### restore_code_block

```python
def restore_code_block(match)
```

**Parameters:**

- `match`

