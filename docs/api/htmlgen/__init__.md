# htmlgen.__init__

**File:** `Application/htmlgen/__init__.py`

## Description

Compartmentalized HTML Generation System for Capcat.

This package implements a modular, configuration-driven HTML generation system
that replaces the monolithic html_generator.py with source-specific generators.

Architecture:
- BaseHTMLGenerator: Abstract base class with common functionality
- Source-specific generators: HN, LessWrong, Lobsters, etc.
- Configuration-driven behavior via YAML files
- Template system with override capability
- Factory pattern for dynamic generator instantiation

Usage:
    from htmlgen import HTMLGeneratorFactory

    # Create generator for specific source
    generator = HTMLGeneratorFactory.create_generator('hn')

    # Generate HTML pages
    html = generator.generate_article_page(markdown_path, title, breadcrumb)

Benefits:
- Maintainable: Each source has isolated logic
- Scalable: Easy to add new sources
- Testable: Sources can be tested independently
- Configurable: Behavior defined in YAML files

## Functions

### get_available_sources

```python
def get_available_sources()
```

Get list of all available source generators.

Returns:
    List of source IDs that have registered generators

### detect_source_from_directory

```python
def detect_source_from_directory(directory_name)
```

Detect which source a directory belongs to based on naming patterns.

Args:
    directory_name: Name of directory to identify

Returns:
    Source ID if match found, None otherwise

**Parameters:**

- `directory_name`

### create_generator

```python
def create_generator(source_id)
```

Create HTML generator for specified source.

Args:
    source_id: Source identifier (e.g., 'hn', 'lesswrong', 'lb')

Returns:
    Source-specific HTML generator instance

Raises:
    ValueError: If source is not registered

**Parameters:**

- `source_id`

