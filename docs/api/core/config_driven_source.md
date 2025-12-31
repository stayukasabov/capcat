# core.source_system.config_driven_source

**File:** `Application/core/source_system/config_driven_source.py`

## Description

Config-driven source implementation.
Handles sources that are defined purely through configuration files.

Refactored for:
- Proper XML parsing with lxml (eliminates XMLParsedAsHTMLWarning)
- Strategy pattern for discovery methods (RSS vs HTML)
- Reduced cyclomatic complexity
- Single Responsibility Principle compliance
- Improved error handling

## Classes

### ConfigDrivenSource

**Inherits from:** BaseSource

Source implementation for config-driven sources.

Uses configuration data to extract articles and content without
requiring custom Python code. Delegates to strategy classes for
different discovery methods (RSS, HTML).

#### Methods

##### source_type

```python
def source_type(self) -> str
```

Return the source type.

**Parameters:**

- `self`

**Returns:** str

##### discover_articles

```python
def discover_articles(self, count: int) -> List[Article]
```

Discover articles using configured discovery method.

Supports both RSS and HTML scraping based on configuration.
Uses Strategy pattern to delegate to appropriate discovery handler.

Args:
    count: Maximum number of articles to discover

Returns:
    List of Article objects

Raises:
    ArticleDiscoveryError: If article discovery fails

**Parameters:**

- `self`
- `count` (int)

**Returns:** List[Article]

##### fetch_article_content

```python
def fetch_article_content(self, article: Article, output_dir: str, progress_callback = None) -> Tuple[bool, Optional[str]]
```

Fetch article content using configured content selectors.

Args:
    article: Article to fetch
    output_dir: Directory to save content
    progress_callback: Optional progress callback function

Returns:
    Tuple of (success, article_path)

Raises:
    ContentFetchError: If content fetching fails

**Parameters:**

- `self`
- `article` (Article)
- `output_dir` (str)
- `progress_callback` *optional*

**Returns:** Tuple[bool, Optional[str]]

##### _prepare_fetcher_config

```python
def _prepare_fetcher_config(self) -> dict
```

Prepare configuration for NewsSourceArticleFetcher.

Returns:
    Configuration dictionary with required fields

**Parameters:**

- `self`

**Returns:** dict

##### _validate_custom_config

```python
def _validate_custom_config(self) -> List[str]
```

Validate config-driven source configuration.

Returns:
    List of validation error messages

**Parameters:**

- `self`

**Returns:** List[str]

##### _should_skip_custom

```python
def _should_skip_custom(self, url: str, title: str = '') -> bool
```

Custom skip logic for config-driven sources.

Args:
    url: URL to check
    title: Optional article title

Returns:
    True if URL should be skipped

**Parameters:**

- `self`
- `url` (str)
- `title` (str) *optional*

**Returns:** bool


