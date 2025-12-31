# scripts.add_doc_navigation

**File:** `Application/scripts/add_doc_navigation.py`

## Description

Add chapter navigation links to documentation HTML files.
Inserts navigation directly into HTML for better SEO and non-JS support.

## Constants

### NAVIGATION_MAP

**Value:** `{'quick-start.html': {'next': {'url': 'configuration.html', 'title': 'Configuration'}}, 'configuration.html': {'next': {'url': 'interactive-mode.html', 'title': 'Interactive Mode'}}, 'interactive-mode.html': {'next': {'url': 'source-management-menu.html', 'title': 'Source Management'}}, 'source-management-menu.html': {'next': {'url': 'source-development.html', 'title': 'Source Development'}}, 'source-development.html': {'next': {'url': 'architecture.html', 'title': 'Architecture Overview'}}, 'architecture.html': {'next': {'url': 'DIAGRAMS_INDEX.html', 'title': 'Architecture Diagrams'}}, 'DIAGRAMS_INDEX.html': {'next': {'url': 'api-reference.html', 'title': 'API Reference'}}, 'api-reference.html': {'next': {'url': 'testing.html', 'title': 'Testing Guide'}}, 'testing.html': {'next': {'url': 'deployment.html', 'title': 'Deployment Guide'}}, 'deployment.html': {'next': {'url': 'ethical-scraping.html', 'title': 'Ethical Scraping Guidelines'}}, 'ethical-scraping.html': {'next': {'url': 'dependencies.html', 'title': 'Dependency Management'}}, 'dependencies.html': {'next': {'url': 'dependency-management.html', 'title': 'Advanced Dependency Management'}}, 'tutorials/user/index.html': {'next': {'url': '01-getting-started.html', 'title': 'Tutorial 1: Getting Started'}}, 'tutorials/user/01-getting-started.html': {'next': {'url': '02-daily-workflow.html', 'title': 'Tutorial 2: Daily Workflow'}}, 'tutorials/user/02-daily-workflow.html': {'next': {'url': '03-interactive-mode.html', 'title': 'Tutorial 3: Interactive Mode'}}, 'tutorials/user/03-interactive-mode.html': {'next': {'url': '04-managing-sources.html', 'title': 'Tutorial 4: Managing Sources'}}, 'tutorials/user/04-managing-sources.html': {'next': {'url': '05-bundles.html', 'title': 'Tutorial 5: Working with Bundles'}}, 'tutorials/user/05-bundles.html': {'next': {'url': '06-customizing-output.html', 'title': 'Tutorial 6: Customizing Output'}}, 'tutorials/01-cli-commands-exhaustive.html': {'next': {'url': '02-interactive-mode-exhaustive.html', 'title': 'Tutorial 2: Interactive Mode (Exhaustive)'}}, 'tutorials/02-interactive-mode-exhaustive.html': {'next': {'url': '03-configuration-exhaustive.html', 'title': 'Tutorial 3: Configuration (Exhaustive)'}}, 'tutorials/03-configuration-exhaustive.html': {'next': {'url': '04-source-system-exhaustive.html', 'title': 'Tutorial 4: Source System (Exhaustive)'}}, 'tutorials/04-source-system-exhaustive.html': {'next': {'url': '05-api-functions-exhaustive.html', 'title': 'Tutorial 5: API Functions (Exhaustive)'}}, 'feature-add-source.html': {'next': {'url': 'feature-remove-source.html', 'title': 'Remove Source Feature'}}, 'feature-remove-source.html': {'next': {'url': 'remove-source-advanced-features.html', 'title': 'Advanced Remove Source Features'}}, 'architecture/index.html': {'next': {'url': 'system.html', 'title': 'System Architecture'}}, 'architecture/system.html': {'next': {'url': 'components.html', 'title': 'Component Architecture'}}, 'diagrams/index.html': {'next': {'url': 'system_architecture.html', 'title': 'System Architecture Diagram'}}, 'diagrams/system_architecture.html': {'next': {'url': 'data_flow.html', 'title': 'Data Flow Diagram'}}, 'diagrams/data_flow.html': {'next': {'url': 'processing_pipeline.html', 'title': 'Processing Pipeline Diagram'}}, 'diagrams/processing_pipeline.html': {'next': {'url': 'source_system.html', 'title': 'Source System Diagram'}}, 'diagrams/source_system.html': {'next': {'url': 'class_diagrams.html', 'title': 'Class Diagrams'}}, 'diagrams/class_diagrams.html': {'next': {'url': 'deployment.html', 'title': 'Deployment Diagram'}}, 'development/index.html': {'next': {'url': '01-architecture-logic.html', 'title': 'Architecture Logic'}}, 'development/01-architecture-logic.html': {'next': {'url': '02-team-onboarding.html', 'title': 'Team Onboarding'}}, 'developer/index.html': {'next': {'url': 'guide.html', 'title': 'Developer Guide'}}}`

## Functions

### generate_navigation_html

```python
def generate_navigation_html(next_url: str, next_title: str) -> str
```

Generate the HTML for chapter navigation.

**Parameters:**

- `next_url` (str)
- `next_title` (str)

**Returns:** str

### get_relative_path

```python
def get_relative_path(file_path: str) -> str
```

Get the relative path from docs directory.

**Parameters:**

- `file_path` (str)

**Returns:** str

### remove_existing_navigation

```python
def remove_existing_navigation(content: str) -> str
```

Remove any existing chapter navigation from HTML.

**Parameters:**

- `content` (str)

**Returns:** str

### add_navigation_to_file

```python
def add_navigation_to_file(file_path: Path, docs_dir: Path) -> bool
```

Add navigation to a single HTML file.

**Parameters:**

- `file_path` (Path)
- `docs_dir` (Path)

**Returns:** bool

### main

```python
def main()
```

Process all documentation HTML files.

