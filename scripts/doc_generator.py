#!/usr/bin/env python3
"""
Documentation Generator for Capcat

Automatically extracts and generates comprehensive documentation from the codebase.
"""

import ast

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class FunctionDoc:
    """Documentation for a function."""
    name: str
    module: str
    file_path: str
    line_number: int
    docstring: Optional[str]
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    decorators: List[str]
    is_public: bool
    complexity_score: int


@dataclass
class ClassDoc:
    """Documentation for a class."""
    name: str
    module: str
    file_path: str
    line_number: int
    docstring: Optional[str]
    methods: List[FunctionDoc]
    attributes: List[Dict[str, Any]]
    inheritance: List[str]
    is_public: bool


@dataclass
class ModuleDoc:
    """Documentation for a module."""
    name: str
    file_path: str
    docstring: Optional[str]
    functions: List[FunctionDoc]
    classes: List[ClassDoc]
    imports: List[str]
    constants: List[Dict[str, Any]]


class CodeAnalyzer:
    """Analyzes Python code to extract documentation information."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.modules: List[ModuleDoc] = []

    def analyze_project(self) -> None:
        """Analyze the entire project structure."""
        python_files = list(self.project_root.rglob("*.py"))

        # Filter out virtual environment, cache, test files, and legacy files (FOSS standard)
        python_files = [
            f for f in python_files
            if "venv" not in str(f)
            and "__pycache__" not in str(f)
            and "/tests/" not in str(f)  # Exclude tests/ directory
            and not f.name.startswith("test_")  # Exclude test_*.py files
            and not f.name.endswith("_test.py")  # Exclude *_test.py files
            and "run_capcat_old" not in f.name  # Exclude legacy run_capcat_old files
            and "Animation-tests" not in str(f)  # Exclude Animation-tests directory
            and "PDF2MD" not in str(f)  # Exclude PDF2MD directory
        ]

        for file_path in python_files:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {e}")

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            module_name = self._get_module_name(file_path)

            module_doc = ModuleDoc(
                name=module_name,
                file_path=str(file_path),
                docstring=ast.get_docstring(tree),
                functions=[],
                classes=[],
                imports=self._extract_imports(tree),
                constants=self._extract_constants(tree)
            )

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not self._is_method(node, tree):
                        func_doc = self._analyze_function(node, module_name, file_path)
                        module_doc.functions.append(func_doc)
                elif isinstance(node, ast.ClassDef):
                    class_doc = self._analyze_class(node, module_name, file_path, content)
                    module_doc.classes.append(class_doc)

            self.modules.append(module_doc)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Get the module name from file path."""
        relative_path = file_path.relative_to(self.project_root)
        module_path = str(relative_path).replace('.py', '').replace('/', '.')
        return module_path

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _extract_constants(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract module-level constants."""
        constants = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append({
                            'name': target.id,
                            'line': node.lineno,
                            'value': ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                        })
        return constants

    def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method of a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False

    def _analyze_function(self, node: ast.FunctionDef, module_name: str, file_path: Path) -> FunctionDoc:
        """Analyze a function definition."""
        return FunctionDoc(
            name=node.name,
            module=module_name,
            file_path=str(file_path),
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            parameters=self._extract_parameters(node),
            return_type=self._extract_return_type(node),
            decorators=self._extract_decorators(node),
            is_public=not node.name.startswith('_'),
            complexity_score=self._calculate_complexity(node)
        )

    def _analyze_class(self, node: ast.ClassDef, module_name: str, file_path: Path, content: str) -> ClassDoc:
        """Analyze a class definition."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = self._analyze_function(item, module_name, file_path)
                methods.append(method_doc)

        return ClassDoc(
            name=node.name,
            module=module_name,
            file_path=str(file_path),
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            methods=methods,
            attributes=self._extract_class_attributes(node),
            inheritance=self._extract_inheritance(node),
            is_public=not node.name.startswith('_')
        )

    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters."""
        params = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation else None,
                'required': True
            }
            params.append(param)

        # Handle defaults
        num_defaults = len(node.args.defaults)
        if num_defaults > 0:
            for i, default in enumerate(node.args.defaults):
                param_index = len(params) - num_defaults + i
                if param_index >= 0:
                    params[param_index]['required'] = False
                    params[param_index]['default'] = ast.unparse(default) if hasattr(ast, 'unparse') else str(default)

        return params

    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract function return type."""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        return None

    def _extract_decorators(self, node: ast.FunctionDef) -> List[str]:
        """Extract function decorators."""
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(ast.unparse(decorator) if hasattr(ast, 'unparse') else str(decorator))
        return decorators

    def _extract_class_attributes(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract class attributes."""
        attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attributes.append({
                    'name': item.target.id,
                    'type': ast.unparse(item.annotation) if item.annotation else None,
                    'line': item.lineno
                })
        return attributes

    def _extract_inheritance(self, node: ast.ClassDef) -> List[str]:
        """Extract class inheritance."""
        inheritance = []
        for base in node.bases:
            inheritance.append(ast.unparse(base) if hasattr(ast, 'unparse') else str(base))
        return inheritance

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


class DocumentationGenerator:
    """Generates various types of documentation."""

    def __init__(self, analyzer: CodeAnalyzer, output_dir: str):
        self.analyzer = analyzer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_all_docs(self) -> None:
        """Generate all documentation types."""
        print("Generating API documentation...")
        self.generate_api_docs()

        print("Generating architecture documentation...")
        self.generate_architecture_docs()

        print("Generating module reference...")
        self.generate_module_reference()

        print("Generating developer guide...")
        self.generate_developer_guide()

        print("Generating README...")
        self.generate_readme()

        print("Generating documentation index...")
        self.generate_index()

    def generate_api_docs(self) -> None:
        """Generate API documentation in markdown format."""
        api_dir = self.output_dir / "api"
        api_dir.mkdir(exist_ok=True)

        # Group modules by package
        packages = {}
        for module in self.analyzer.modules:
            package_name = module.name.split('.')[0]
            if package_name not in packages:
                packages[package_name] = []
            packages[package_name].append(module)

        # Generate documentation for each package
        for package_name, modules in packages.items():
            self._generate_package_docs(package_name, modules, api_dir)

        # Generate API index
        self._generate_api_index(packages, api_dir)

    def _generate_package_docs(self, package_name: str, modules: List[ModuleDoc], api_dir: Path) -> None:
        """Generate documentation for a package."""
        package_dir = api_dir / package_name
        package_dir.mkdir(exist_ok=True)

        # Package overview
        overview_content = f"""# {package_name.title()} Package

## Overview

This package contains the following modules:

"""

        for module in modules:
            overview_content += f"- [`{module.name}`](./{module.name.split('.')[-1]}.md)"
            if module.docstring:
                overview_content += f" - {module.docstring.split('.')[0]}"
            overview_content += "\n"

        with open(package_dir / "README.md", 'w') as f:
            f.write(overview_content)

        # Individual module documentation
        for module in modules:
            self._generate_module_docs(module, package_dir)

    def _generate_module_docs(self, module: ModuleDoc, package_dir: Path) -> None:
        """Generate documentation for a single module."""
        module_name = module.name.split('.')[-1]
        # Convert absolute path to relative Application/ path
        file_path = module.file_path
        if self.analyzer.project_root.name == "Application":
            try:
                relative_path = Path(file_path).relative_to(self.analyzer.project_root)
                file_path = f"Application/{relative_path}"
            except ValueError:
                # If path is not relative to project root, use basename only
                file_path = Path(file_path).name

        content = f"""# {module.name}

**File:** `{file_path}`

"""

        if module.docstring:
            content += f"""## Description

{module.docstring}

"""

        # Constants
        if module.constants:
            content += "## Constants\n\n"
            for const in module.constants:
                content += f"### {const['name']}\n\n"
                content += f"**Value:** `{const['value']}`\n\n"

        # Classes
        if module.classes:
            content += "## Classes\n\n"
            for cls in module.classes:
                content += self._format_class_docs(cls)

        # Functions (include private for contributors - FOSS standard)
        if module.functions:
            content += "## Functions\n\n"
            for func in module.functions:
                content += self._format_function_docs(func)

        with open(package_dir / f"{module_name}.md", 'w') as f:
            f.write(content)

    def _format_class_docs(self, cls: ClassDoc) -> str:
        """Format class documentation."""
        content = f"### {cls.name}\n\n"

        if cls.inheritance:
            content += f"**Inherits from:** {', '.join(cls.inheritance)}\n\n"

        if cls.docstring:
            content += f"{cls.docstring}\n\n"

        # Methods (include private for contributors - FOSS standard)
        if cls.methods:
            content += "#### Methods\n\n"
            for method in cls.methods:
                content += self._format_function_docs(method, is_method=True)

        return content + "\n"

    def _format_function_docs(self, func: FunctionDoc, is_method: bool = False) -> str:
        """Format function documentation."""
        indent = "#####" if is_method else "###"
        content = f"{indent} {func.name}\n\n"

        # Signature
        params = []
        for param in func.parameters:
            param_str = param['name']
            if param['type']:
                param_str += f": {param['type']}"
            if not param['required'] and 'default' in param:
                param_str += f" = {param['default']}"
            params.append(param_str)

        signature = f"def {func.name}({', '.join(params)})"
        if func.return_type:
            signature += f" -> {func.return_type}"

        content += f"```python\n{signature}\n```\n\n"

        if func.docstring:
            content += f"{func.docstring}\n\n"

        # Parameters
        if func.parameters:
            content += "**Parameters:**\n\n"
            for param in func.parameters:
                content += f"- `{param['name']}`"
                if param['type']:
                    content += f" ({param['type']})"
                if not param['required']:
                    content += " *optional*"
                content += "\n"
            content += "\n"

        # Return type
        if func.return_type:
            content += f"**Returns:** {func.return_type}\n\n"

        # Complexity indicator
        if func.complexity_score > 10:
            content += f"⚠️ **High complexity:** {func.complexity_score}\n\n"

        return content

    def _generate_api_index(self, packages: Dict[str, List[ModuleDoc]], api_dir: Path) -> None:
        """Generate API documentation index."""
        content = """# API Reference

This is the complete API reference for Capcat.

## Packages

"""

        for package_name in sorted(packages.keys()):
            content += f"- [{package_name.title()}](./{package_name}/README.md)\n"

        content += """
## Quick Navigation

### Core Components

- [capcat](./capcat.md) - Main application entry point
- [cli](./cli.md) - Command-line interface
- [core.config](./core/config.md) - Configuration management
- [core.article_fetcher](./core/article_fetcher.md) - Article processing

### Source System

- [core.source_system](./core/source_system/README.md) - Source management framework
- [sources.active](./sources/active/README.md) - Active news sources

### Media Processing

- [core.unified_media_processor](./core/unified_media_processor.md) - Media handling
- [core.formatter](./core/formatter.md) - Content formatting

"""

        with open(api_dir / "README.md", 'w') as f:
            f.write(content)

    def generate_architecture_docs(self) -> None:
        """Generate architecture documentation with diagrams."""
        arch_dir = self.output_dir / "architecture"
        arch_dir.mkdir(exist_ok=True)

        # System architecture
        system_arch = """# System Architecture

## Overview

Capcat is a modular news article archiving system designed for scalability and extensibility.

## Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface"
        CLI[CLI Interface]
        Wrapper[Bash Wrapper]
    end

    subgraph "Core Application"
        Main[capcat.py]
        Config[Configuration]
        Progress[Progress Tracking]
    end

    subgraph "Source System"
        Factory[Source Factory]
        Registry[Source Registry]
        ConfigDriven[Config-Driven Sources]
        Custom[Custom Sources]
    end

    subgraph "Processing Pipeline"
        Fetcher[Article Fetcher]
        MediaProc[Media Processor]
        Formatter[Content Formatter]
        HTMLGen[HTML Generator]
    end

    subgraph "Storage"
        FileSystem[File System]
        Markdown[Markdown Files]
        Media[Media Files]
        HTML[HTML Output]
    end

    CLI --> Main
    Wrapper --> Main
    Main --> Config
    Main --> Progress
    Main --> Factory
    Factory --> Registry
    Registry --> ConfigDriven
    Registry --> Custom
    Factory --> Fetcher
    Fetcher --> MediaProc
    MediaProc --> Formatter
    Formatter --> HTMLGen
    HTMLGen --> FileSystem
    Fetcher --> Markdown
    MediaProc --> Media
    HTMLGen --> HTML
```

## Component Responsibilities

### Core Application Layer

- **capcat.py**: Main application orchestrator
- **cli.py**: Command-line argument parsing and validation
- **core.config**: Configuration management and validation

### Source System

- **Source Factory**: Creates and manages source instances
- **Source Registry**: Auto-discovers and registers available sources
- **Config-Driven Sources**: YAML-configured simple sources
- **Custom Sources**: Python-implemented complex sources with comments

### Processing Pipeline

- **Article Fetcher**: Downloads and processes article content
- **Media Processor**: Handles images, videos, and other media
- **Content Formatter**: Converts HTML to Markdown
- **HTML Generator**: Creates browsable HTML versions

## Design Patterns

### Factory Pattern
Used for source creation to support multiple source types.

### Registry Pattern
Auto-discovery and registration of available sources.

### Template Method Pattern
Base classes define processing flow, subclasses implement specifics.

### Observer Pattern
Progress tracking and logging throughout the pipeline.

## Data Flow

1. **Input**: User specifies sources and parameters via CLI
2. **Source Resolution**: Factory creates appropriate source instances
3. **Article Discovery**: Sources fetch article lists
4. **Content Processing**: Articles downloaded and processed in parallel
5. **Media Handling**: Images and media downloaded and organized
6. **Output Generation**: Markdown and HTML files created
7. **Storage**: Files organized in structured directory hierarchy

## Scalability Considerations

- **Parallel Processing**: ThreadPoolExecutor for concurrent article processing
- **Session Pooling**: Shared HTTP connections for performance
- **Modular Sources**: Easy addition of new sources without core changes
- **Configurable Limits**: Rate limiting and resource management

"""

        with open(arch_dir / "system.md", 'w') as f:
            f.write(system_arch)

        # Component details
        self._generate_component_docs(arch_dir)

    def _generate_component_docs(self, arch_dir: Path) -> None:
        """Generate detailed component documentation."""
        components_content = """# Component Details

## Source System Components

### Source Factory (`core.source_system.source_factory`)

Responsible for creating source instances based on configuration.

**Key Methods:**
- `create_source(source_name: str)` - Creates source instance
- `get_available_sources()` - Lists all available sources
- `validate_source(source_name: str)` - Validates source configuration

### Source Registry (`core.source_system.source_registry`)

Auto-discovers and manages available sources.

**Discovery Process:**
1. Scans `sources/active/` directory
2. Loads YAML configs for config-driven sources
3. Imports Python modules for custom sources
4. Validates source implementations
5. Registers sources with metadata

### Base Source (`core.source_system.base_source`)

Abstract base class defining the source interface.

**Required Methods:**
- `get_articles(count: int)` - Fetch article list
- `get_article_content(url: str)` - Download article content

## Processing Components

### Article Fetcher (`core.article_fetcher`)

Coordinates the article processing pipeline.

**Responsibilities:**
- Parallel article processing
- Error handling and retry logic
- Progress tracking
- Resource management

### Media Processor (`core.unified_media_processor`)

Handles all media-related operations.

**Features:**
- Image downloading and optimization
- Video/audio handling (with --media flag)
- Media type detection
- File organization

### Content Formatter (`core.formatter`)

Converts HTML content to Markdown.

**Processing Steps:**
1. HTML parsing and cleaning
2. Image reference extraction
3. Link processing
4. Markdown conversion
5. Content sanitization

## Configuration Components

### Configuration Manager (`core.config`)

Centralized configuration management.

**Configuration Sources:**
1. Command-line arguments (highest priority)
2. Environment variables
3. Config files (`capcat.yml`)
4. Default values (lowest priority)

### Source Configuration (`core.source_config`)

Source-specific configuration and metadata.

**Source Types:**
- **Config-Driven**: YAML-based configuration
- **Custom**: Python implementation with full control

"""

        with open(arch_dir / "components.md", 'w') as f:
            f.write(components_content)

    def generate_module_reference(self) -> None:
        """Generate complete module reference."""
        ref_dir = self.output_dir / "reference"
        ref_dir.mkdir(exist_ok=True)

        # Generate module index
        content = """# Module Reference

Complete reference of all modules, classes, and functions in Capcat.

## Modules by Package

"""

        # Group by package
        packages = {}
        for module in self.analyzer.modules:
            package = module.name.split('.')[0] if '.' in module.name else 'root'
            if package not in packages:
                packages[package] = []
            packages[package].append(module)

        for package_name in sorted(packages.keys()):
            content += f"\n### {package_name.title()}\n\n"
            for module in sorted(packages[package_name], key=lambda m: m.name):
                content += f"- [{module.name}](../api/{package_name}/{module.name.split('.')[-1]}.md)"
                if module.docstring:
                    first_line = module.docstring.split('.')[0]
                    content += f" - {first_line}"
                content += "\n"

        # Add statistics
        total_functions = sum(len(m.functions) for m in self.analyzer.modules)
        total_classes = sum(len(m.classes) for m in self.analyzer.modules)
        public_functions = sum(len([f for f in m.functions if f.is_public]) for m in self.analyzer.modules)

        content += f"""
## Statistics

- **Total Modules**: {len(self.analyzer.modules)}
- **Total Classes**: {total_classes}
- **Total Functions**: {total_functions}
- **Public Functions**: {public_functions}
- **Documentation Coverage**: {(public_functions / max(total_functions, 1)) * 100:.1f}%

"""

        with open(ref_dir / "modules.md", 'w') as f:
            f.write(content)

    def generate_developer_guide(self) -> None:
        """Generate developer guide."""
        dev_dir = self.output_dir / "developer"
        dev_dir.mkdir(exist_ok=True)

        guide_content = """# Developer Guide

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- git

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd capcat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
./capcat list sources
```

## Project Structure

```
Application/
├── capcat.py              # Main application entry point
├── capcat                 # Bash wrapper script
├── run_capcat.py          # Python wrapper
├── cli.py                 # Command-line interface
├── core/                  # Core functionality
│   ├── source_system/     # Source management framework
│   ├── config.py          # Configuration management
│   ├── article_fetcher.py # Article processing
│   └── unified_media_processor.py  # Media handling
├── sources/               # News source implementations
│   ├── active/           # Active sources
│   │   ├── config_driven/ # YAML-configured sources
│   │   └── custom/        # Python-implemented sources
│   └── base/             # Base classes and schemas
├── htmlgen/              # HTML generation system
├── themes/               # CSS themes for HTML output
└── docs/                 # Documentation
```

## Development Workflow

### Adding a New Source

#### Option 1: Config-Driven Source (Simple)

1. Create YAML configuration:

```yaml
# sources/active/config_driven/configs/newsource.yaml
display_name: "New Source"
base_url: "https://newsource.com/"
category: tech
article_selectors: [".headline a"]
content_selectors: [".article-content"]
```

2. Verify the source:

```bash
./capcat fetch newsource --count 5
```

#### Option 2: Custom Source (Advanced)

1. Create source directory:

```bash
mkdir -p sources/active/custom/newsource
```

2. Implement source class:

```python
# sources/active/custom/newsource/source.py
from core.source_system.base_source import BaseSource

class NewSource(BaseSource):
    def __init__(self):
        super().__init__()
        self.name = "newsource"
        self.display_name = "New Source"

    def get_articles(self, count=30):
        # Implementation here
        pass

    def get_article_content(self, url):
        # Implementation here
        pass
```

3. Validate implementation:

```bash
./capcat fetch newsource --count 5
```

### Code Style Guidelines

Follow PEP 8 standards:

- 4 spaces for indentation
- Maximum line length: 79 characters
- Use descriptive variable names
- Add type hints to function signatures
- Write docstrings for all public functions

Example:

```python
def process_article(url: str, output_dir: Path) -> Optional[Article]:
    \"\"\"
    Process a single article from URL.

    Args:
        url: Article URL to process
        output_dir: Directory for output files

    Returns:
        Article object if successful, None otherwise

    Raises:
        SourceError: If article cannot be fetched
        FileSystemError: If output cannot be written
    \"\"\"
    # Implementation here
    pass
```

### Development Validation

Verify your changes work correctly:

```bash
# Fetch from source
./capcat fetch sourcename --count 5

# Try bundle
./capcat bundle tech --count 10
```

### Documentation

Update documentation when making changes:

```bash
# Generate documentation
python scripts/doc_generator.py

# Update architecture diagrams
python scripts/generate_diagrams.py
```

### Debugging

Enable debug logging:

```bash
# Enable debug mode
export CAPCAT_DEBUG=1
./capcat fetch hn --count 5

# Or use Python directly
python capcat.py --debug fetch hn --count 5
```

Common debugging techniques:

1. **Source Issues**: Check robots.txt and rate limiting
2. **Media Problems**: Verify URLs and file permissions
3. **HTML Parsing**: Use browser dev tools to inspect selectors
4. **Performance**: Profile with `cProfile` for bottlenecks

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes following the guidelines
4. Update documentation as needed
5. Commit with descriptive messages
6. Push to your fork and create a pull request

### Performance Considerations

- **Parallel Processing**: Use ThreadPoolExecutor for concurrent operations
- **Session Pooling**: Reuse HTTP connections via SessionPool
- **Rate Limiting**: Respect source rate limits (1 req/10 sec default)
- **Memory Usage**: Process articles in batches for large collections
- **Caching**: Implement caching for frequently accessed data

### Error Handling

Implement comprehensive error handling:

```python
from core.exceptions import SourceError, FileSystemError

try:
    article = fetch_article(url)
except SourceError as e:
    logger.error(f"Source error: {e}")
    return None
except FileSystemError as e:
    logger.error(f"File system error: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    return None
```

### Security Considerations

- Validate all external inputs
- Sanitize HTML content before processing
- Use secure file paths (avoid path traversal)
- Implement rate limiting to prevent abuse
- Follow ethical scraping guidelines

"""

        with open(dev_dir / "guide.md", 'w') as f:
            f.write(guide_content)

    def generate_readme(self) -> None:
        """Generate comprehensive README."""
        readme_content = """# Capcat - News Article Archiving System

A powerful, modular news article archiving system that fetches articles from 13+ sources, converts them to Markdown, and organizes them with media files.

##  Features

- **Multi-Source Support**: 13+ news sources including Hacker News, BBC, Nature, IEEE
- **Modular Architecture**: Easy to add new sources with config-driven or custom implementations
- **Media Handling**: Automatic download and organization of images, videos, and documents
- **Flexible Output**: Markdown files with optional HTML generation
- **Parallel Processing**: Concurrent article processing for performance
- **Privacy Compliant**: Usernames anonymized, no personal data stored
- **Configurable**: Command-line arguments, environment variables, and config files

##  Requirements

- Python 3.8+
- Internet connection for article fetching
- ~100MB disk space for dependencies

##  Installation

### Quick Setup

```bash
# Clone repository
git clone <repository-url>
cd capcat

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify installation
./capcat list sources
```

### Docker (Alternative)

```bash
docker build -t capcat .
docker run -v $(pwd)/output:/app/output capcat bundle tech --count 10
```

##  Quick Start

```bash
# Fetch 10 tech articles
./capcat bundle tech --count 10

# Fetch from specific sources
./capcat fetch hn,bbc --count 15 --media

# Single article processing
./capcat single https://example.com/article

# List available sources
./capcat list sources

# Show bundles
./capcat list bundles
```

##  Usage

### Command Line Interface

```bash
# Basic usage
./capcat <command> [options]

# Commands
list sources           # Show all available sources
list bundles          # Show predefined source bundles
fetch <sources>       # Fetch from specific sources
bundle <name>         # Fetch from predefined bundle
single <url>          # Process single article

# Options
--count N             # Number of articles (default: 30)
--media               # Download videos/audio/documents
--html                # Generate HTML output
--output-dir DIR      # Custom output directory
--config FILE         # Custom config file
--debug               # Enable debug logging
```

### Available Sources

**Technology:**
- `hn` - Hacker News
- `lb` - Lobsters
- `iq` - InfoQ
- `ieee` - IEEE Spectrum
- `mashable` - Mashable

**News:**
- `bbc` - BBC News
- `guardian` - The Guardian

**Science:**
- `nature` - Nature News
- `scientificamerican` - Scientific American

**AI/ML:**
- `mitnews` - MIT News

**Sports:**
- `bbcsport` - BBC Sport

### Predefined Bundles

```bash
./capcat bundle tech          # ieee + mashable
./capcat bundle techpro       # hn + lb + iq
./capcat bundle news          # bbc + guardian
./capcat bundle science       # nature + scientificamerican
./capcat bundle ai            # mitnews
./capcat bundle sports        # bbcsport
```

##  Output Structure

### Batch Processing
```
../News/news_DD-MM-YYYY/
├── Source_DD-MM-YYYY/
│   └── NN_Article_Title/
│       ├── article.md
│       ├── images/
│       ├── files/
│       └── html/ (if --html)
```

### Single Articles
```
../Capcats/cc_DD-MM-YYYY-Title/
├── article.md
├── images/
└── files/
```

##  Configuration

### Command Line (Highest Priority)
```bash
./capcat fetch hn --count 20 --media
```

### Environment Variables
```bash
export CAPCAT_OUTPUT_DIR="/custom/path"
export CAPCAT_DEFAULT_COUNT=50
```

### Config File (`capcat.yml`)
```yaml
output_dir: "/custom/path"
default_count: 50
media_download: true
sources:
  hn:
    rate_limit: 5
```

##  Development

### Adding a New Source

#### Config-Driven (15-30 minutes)
```yaml
# sources/active/config_driven/configs/newsource.yaml
display_name: "New Source"
base_url: "https://newsource.com/"
category: tech
article_selectors: [".headline a"]
content_selectors: [".article-content"]
```

#### Custom Implementation (2-4 hours)
```python
# sources/active/custom/newsource/source.py
from core.source_system.base_source import BaseSource

class NewSource(BaseSource):
    def get_articles(self, count=30):
        # Custom implementation
        pass
```

### Verification
```bash
# Verify all sources work
./capcat list sources

# Verify specific source
./capcat fetch newsource --count 5

# Verify bundle
./capcat bundle tech --count 10
```

##  Architecture

```mermaid
graph TB
    CLI[CLI Interface] --> Main[Main App]
    Main --> Factory[Source Factory]
    Factory --> Sources[News Sources]
    Sources --> Fetcher[Article Fetcher]
    Fetcher --> Media[Media Processor]
    Media --> Format[Content Formatter]
    Format --> Output[File Output]
```

**Key Components:**
- **Source System**: Modular source management with auto-discovery
- **Processing Pipeline**: Parallel article processing with error handling
- **Media Handling**: Intelligent media download and organization
- **Output Generation**: Markdown and HTML with structured directories

##  Common Issues & Solutions

### Module Not Found
```bash
# Use wrapper (handles venv automatically)
./capcat list sources

# Or activate manually
source venv/bin/activate
```

### Source Failures
- 90% success rate is normal (anti-bot protection)
- Some sources may have temporary issues
- Check debug logs for details

### Performance Issues
```bash
# Reduce parallel workers
export CAPCAT_MAX_WORKERS=4

# Enable progress tracking
./capcat fetch hn --count 10 --debug
```

##  Documentation

- [API Reference](docs/api/README.md) - Complete API documentation
- [Architecture Guide](docs/architecture/system.md) - System design details
- [Developer Guide](docs/developer/guide.md) - Contributing and development
- [Source Development](docs/developer/sources.md) - Adding new sources

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Follow PEP 8 coding standards
4. Update documentation
5. Submit pull request

## License

MIT-Style Non-Commercial License - see [LICENSE.txt](../LICENSE.txt) file for details.

**Copyright (c) 2025 Stayu Kasabov**

- Non-commercial use only
- Attribution required
- Share-alike modifications
- Contributions welcome

## Acknowledgments

- Built with Python 3.8+
- Uses BeautifulSoup4 for HTML parsing
- Requests library for HTTP handling
- Threading for parallel processing

##  Support

- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting guide

---

**Note**: This tool is designed for personal archiving and research purposes. Please respect robots.txt and terms of service for all sources.
"""

        with open(self.output_dir / "README.md", 'w') as f:
            f.write(readme_content)

    def generate_index(self) -> None:
        """Generate documentation index."""
        index_content = """# Capcat Documentation

Welcome to the comprehensive documentation for Capcat, a modular news article archiving system.

##  Documentation Sections

###  Getting Started
- [README](README.md) - Quick start and overview
- [Installation Guide](developer/guide.md#setup-development-environment) - Detailed setup instructions
- [Usage Examples](README.md#usage) - Common usage patterns

###  Architecture & Design
- [System Architecture](architecture/system.md) - High-level system design
- [Component Details](architecture/components.md) - Detailed component documentation
- [Design Patterns](architecture/system.md#design-patterns) - Architectural patterns used

###  API Reference
- [API Overview](api/README.md) - Complete API documentation
- [Core Modules](api/core/README.md) - Core functionality reference
- [Source System](api/sources/README.md) - Source management APIs

###  Development
- [Developer Guide](developer/guide.md) - Complete development guide
- [Adding Sources](developer/guide.md#adding-a-new-source) - How to add new sources
- [Testing Guide](developer/guide.md#testing) - Testing procedures

###  Reference
- [Module Reference](reference/modules.md) - Complete module listing
- [Configuration Reference](developer/guide.md#configuration) - All configuration options
- [CLI Reference](README.md#command-line-interface) - Command-line usage

##  Quick Navigation

### For Users
- **Getting Started**: [README](README.md) → [Usage](README.md#usage)
- **Configuration**: [Config Guide](developer/guide.md#configuration)
- **Troubleshooting**: [Common Issues](README.md#common-issues--solutions)

### For Developers
- **Setup**: [Development Environment](developer/guide.md#setup-development-environment)
- **Architecture**: [System Design](architecture/system.md)
- **API Docs**: [Core APIs](api/core/README.md)
- **Contributing**: [Development Workflow](developer/guide.md#development-workflow)

### For Administrators
- **Installation**: [Setup Guide](developer/guide.md#prerequisites)
- **Configuration**: [Config Management](developer/guide.md#configuration)
- **Monitoring**: [Performance Considerations](developer/guide.md#performance-considerations)

##  Project Statistics

This documentation was auto-generated and contains:

- **Total Modules**: Comprehensive coverage of all Python modules
- **API Documentation**: Complete function and class references
- **Architecture Diagrams**: Visual system representations
- **Code Examples**: Practical usage demonstrations

##  Documentation Updates

This documentation is automatically generated from the source code. To update:

```bash
python scripts/doc_generator.py
```

Last generated: $(date)

---

**Need help?** Check the [Developer Guide](developer/guide.md) or create an issue on GitHub.
"""

        with open(self.output_dir / "index.md", 'w') as f:
            f.write(index_content)


def main():
    """Main documentation generation function."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "docs")

    print("Analyzing codebase...")
    analyzer = CodeAnalyzer(project_root)
    analyzer.analyze_project()

    print(f"Found {len(analyzer.modules)} modules")

    print("Generating documentation...")
    generator = DocumentationGenerator(analyzer, output_dir)
    generator.generate_all_docs()

    print(f"Documentation generated in: {output_dir}")
    print("Open docs/index.md to get started!")


if __name__ == "__main__":
    main()