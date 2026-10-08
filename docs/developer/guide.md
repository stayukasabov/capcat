---
layout: default
render_with_liquid: false
---

# Developer Guide

## Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- git

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd capcat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
capcat list sources
```

## Project Structure

```
Application/
├── capcat/                    # Main package
│   ├── __init__.py            # Version and entry point
│   ├── cli.py                 # CLI entry point, Global Settings template
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── article_fetcher.py # Article processing
│   │   ├── unified_article_processor.py
│   │   ├── unified_media_processor.py
│   │   ├── source_system/     # Source management framework
│   │   └── config/            # Config subsystem
│   ├── sources/               # News source implementations
│   │   └── builtin/
│   │       ├── config_driven/ # YAML-configured sources
│   │       ├── custom/        # Python-implemented sources (hn, lb, etc.)
│   │       └── bundles.yml    # Bundle definitions
│   └── htmlgen/               # HTML generation system
├── tests/                     # Test suite
├── scripts/                   # Build and doc generation scripts
├── docs/                      # Documentation (GitHub Pages)
├── pyproject.toml
└── README.md
```

## Development Workflow

### Adding a New Source

#### Option 1: Config-Driven Source (Simple)

1. Create YAML configuration:

```yaml
# capcat/sources/builtin/config_driven/configs/newsource.yaml
display_name: "New Source"
base_url: "https://newsource.com/"
category: tech
article_selectors: [".headline a"]
content_selectors: [".article-content"]
```

2. Verify the source:

```bash
capcat fetch newsource --count 5
```

#### Option 2: Custom Source (Advanced)

1. Create source directory:

```bash
mkdir -p capcat/sources/builtin/custom/newsource
```

2. Implement source class:

```python
# capcat/sources/builtin/custom/newsource/source.py
from capcat.core.source_system.base_source import BaseSource

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
capcat fetch newsource --count 5
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
    """
    Process a single article from URL.

    Args:
        url: Article URL to process
        output_dir: Directory for output files

    Returns:
        Article object if successful, None otherwise

    Raises:
        SourceError: If article cannot be fetched
        FileSystemError: If output cannot be written
    """
    # Implementation here
    pass
```

### Development Validation

Verify your changes work correctly:

```bash
# Fetch from source
capcat fetch sourcename --count 5

# Try bundle
capcat bundle tech --count 10
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
capcat fetch hn --count 5

# Or use Python directly
python -m capcat --debug fetch hn --count 5
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
from capcat.core.exceptions import SourceError, FileSystemError

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

