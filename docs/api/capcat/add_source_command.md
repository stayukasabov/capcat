---
layout: default
render_with_liquid: false
---

# capcat.core.source_system.add_source_command

**File:** `Application/capcat/core/source_system/add_source_command.py`

## Description

Professional implementation of the add-source command using clean architecture principles.
Separates concerns through dependency injection and follows SOLID principles.

## Classes

### SourceMetadata

Value object containing all source metadata.

#### Methods

##### validate

```python
def validate(self) -> None
```

Validate source metadata.

**Parameters:**

- `self`

**Returns:** None


### FeedIntrospector

**Inherits from:** Protocol

Protocol for RSS feed introspection.

Implementations read a feed URL and expose its title and base URL.
See ``RssFeedIntrospector`` for the production implementation.

#### Methods

##### feed_title

```python
def feed_title(self) -> str
```

Human-readable title extracted from the RSS/Atom feed.

**Parameters:**

- `self`

**Returns:** str

##### base_url

```python
def base_url(self) -> str
```

Root URL of the publisher (stripped of path).

**Parameters:**

- `self`

**Returns:** str


### UserInterface

**Inherits from:** Protocol

Protocol for user interaction during the add-source workflow.

Implementations may use questionary (interactive TUI), a mock (tests),
or any other mechanism that satisfies this contract.

#### Methods

##### get_display_name

```python
def get_display_name(self, suggested: str) -> str
```

Prompt the user to confirm or override the suggested display name.

Args:
    suggested: Feed title extracted from the RSS feed.

Returns:
    The confirmed or overridden display name string.

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### get_source_id

```python
def get_source_id(self, suggested: str) -> str
```

Prompt the user to confirm or override the suggested source ID.

Args:
    suggested: Auto-derived source ID (e.g. ``"mysite"``).

Returns:
    The confirmed or overridden source ID string.

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### select_category

```python
def select_category(self, categories: List[str]) -> str
```

Prompt the user to choose a topic category.

Args:
    categories: Available category names.

Returns:
    The selected category string.

**Parameters:**

- `self`
- `categories` (List[str])

**Returns:** str

##### get_article_count

```python
def get_article_count(self) -> int
```

Prompt user for articles per run. Default: 30.

Returns:
    Positive integer article count.

**Parameters:**

- `self`

**Returns:** int

##### confirm_bundle_addition

```python
def confirm_bundle_addition(self) -> bool
```

Ask whether to add the new source to an existing bundle.

Returns:
    ``True`` if the user wants to add to a bundle.

**Parameters:**

- `self`

**Returns:** bool

##### select_bundle

```python
def select_bundle(self, bundles: List[str]) -> Optional[str]
```

Prompt the user to pick a bundle to add the source to.

Args:
    bundles: Available bundle names.

Returns:
    Selected bundle name, or ``None`` if cancelled.

**Parameters:**

- `self`
- `bundles` (List[str])

**Returns:** Optional[str]

##### confirm_test_fetch

```python
def confirm_test_fetch(self) -> bool
```

Ask whether to run a test fetch after saving the config.

Returns:
    ``True`` if the user wants a test fetch.

**Parameters:**

- `self`

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

Display a success notification.

Args:
    message: Success text to show the user.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

Display an error notification.

Args:
    message: Error text to show the user.

**Parameters:**

- `self`
- `message` (str)

**Returns:** None


### ConfigGenerator

**Inherits from:** Protocol

Protocol for configuration file generation.

#### Methods

##### generate_and_save

```python
def generate_and_save(self, metadata: SourceMetadata, config_path: Path) -> Path
```

Generate a YAML config file and write it to disk.

Args:
    metadata: Source metadata to serialize.
    config_path: Directory where the config file should be saved.

Returns:
    Path to the written config file.

**Parameters:**

- `self`
- `metadata` (SourceMetadata)
- `config_path` (Path)

**Returns:** Path


### BundleManager

**Inherits from:** Protocol

Protocol for bundle management.

#### Methods

##### get_bundle_names

```python
def get_bundle_names(self) -> List[str]
```

Return the names of all available bundles.

Returns:
    List of bundle name strings.

**Parameters:**

- `self`

**Returns:** List[str]

##### add_source_to_bundle

```python
def add_source_to_bundle(self, source_id: str, bundle_name: str) -> None
```

Add a source to a named bundle in bundles.yml.

Args:
    source_id: Source identifier to add.
    bundle_name: Bundle to add the source to.

**Parameters:**

- `self`
- `source_id` (str)
- `bundle_name` (str)

**Returns:** None


### SourceTester

**Inherits from:** Protocol

Protocol for testing new sources.

#### Methods

##### test_source

```python
def test_source(self, source_id: str, count: int = 1) -> bool
```

Run a test fetch to verify the source is functional.

Args:
    source_id: The source identifier to test.
    count: Number of articles to attempt fetching.

Returns:
    ``True`` if at least one article was fetched successfully.

**Parameters:**

- `self`
- `source_id` (str)
- `count` (int) *optional*

**Returns:** bool


### CategoryProvider

**Inherits from:** Protocol

Protocol for category management.

#### Methods

##### get_available_categories

```python
def get_available_categories(self) -> List[str]
```

Return all available topic category names.

Returns:
    List of category strings (e.g. ``["tech", "science", "news"]``).

**Parameters:**

- `self`

**Returns:** List[str]


### AddSourceCommand

Command to add a new RSS source using clean architecture principles.

Follows SOLID principles:
- Single Responsibility: Only orchestrates the add-source workflow
- Open/Closed: Extensible through dependency injection
- Liskov Substitution: Uses protocols for type safety
- Interface Segregation: Small, focused protocols
- Dependency Inversion: Depends on abstractions, not concretions

#### Methods

##### __init__

```python
def __init__(self, introspector_factory: 'IntrospectorFactory', ui: UserInterface, config_generator: ConfigGenerator, bundle_manager: BundleManager, source_tester: SourceTester, category_provider: CategoryProvider, config_path: Path, bundles_path: Path, logger: Optional[Any] = None) -> None
```

Wire up all dependencies for the add-source workflow.

Args:
    introspector_factory: Creates FeedIntrospector instances for URLs.
    ui: User interaction layer (questionary, mock, etc.).
    config_generator: Writes YAML config files to disk.
    bundle_manager: Reads and updates bundles.yml.
    source_tester: Runs test fetches against new sources.
    category_provider: Returns available topic categories.
    config_path: Directory where new source configs are saved.
    bundles_path: Path to bundles.yml.
    logger: Optional logger; defaults to module logger.

**Parameters:**

- `self`
- `introspector_factory` ('IntrospectorFactory')
- `ui` (UserInterface)
- `config_generator` (ConfigGenerator)
- `bundle_manager` (BundleManager)
- `source_tester` (SourceTester)
- `category_provider` (CategoryProvider)
- `config_path` (Path)
- `bundles_path` (Path)
- `logger` (Optional[Any]) *optional*

**Returns:** None

##### execute

```python
def execute(self, url: str) -> Path
```

Execute the add-source command.

Args:
    url: RSS feed URL to add

Returns:
    Path to the written config file.

Raises:
    CapcatError: If any step in the process fails

**Parameters:**

- `self`
- `url` (str)

**Returns:** Path

##### _introspect_feed

```python
def _introspect_feed(self, url: str) -> FeedIntrospector
```

Step 1: Introspect the RSS feed.

**Parameters:**

- `self`
- `url` (str)

**Returns:** FeedIntrospector

##### _collect_source_metadata

```python
def _collect_source_metadata(self, introspector: FeedIntrospector, url: str) -> SourceMetadata
```

Step 2: Collect all required metadata from user and introspector.

**Parameters:**

- `self`
- `introspector` (FeedIntrospector)
- `url` (str)

**Returns:** SourceMetadata

##### _generate_configuration

```python
def _generate_configuration(self, metadata: SourceMetadata) -> Path
```

Step 3: Generate and save configuration file.

**Parameters:**

- `self`
- `metadata` (SourceMetadata)

**Returns:** Path

##### _handle_bundle_integration

```python
def _handle_bundle_integration(self, source_id: str) -> None
```

Step 4: Handle optional bundle integration.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** None

##### _handle_source_testing

```python
def _handle_source_testing(self, source_id: str) -> None
```

Step 5: Handle optional source testing.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** None

##### _generate_source_id_suggestion

```python
def _generate_source_id_suggestion(self, feed_title: str) -> str
```

Generate a suggested source ID from feed title.

**Parameters:**

- `self`
- `feed_title` (str)

**Returns:** str


### IntrospectorFactory

**Inherits from:** Protocol

Factory for creating feed introspectors.

#### Methods

##### create

```python
def create(self, url: str) -> FeedIntrospector
```

Create a FeedIntrospector for the given feed URL.

Args:
    url: RSS/Atom feed URL to introspect.

Returns:
    A FeedIntrospector instance ready to expose feed metadata.

**Parameters:**

- `self`
- `url` (str)

**Returns:** FeedIntrospector


### RssFeedIntrospectorAdapter

Adapter to make existing RssFeedIntrospector compatible with protocol.

#### Methods

##### __init__

```python
def __init__(self, introspector)
```

Wrap an existing RssFeedIntrospector instance.

Args:
    introspector: An ``RssFeedIntrospector`` instance whose
        ``feed_title`` and ``base_url`` attributes will be proxied.

**Parameters:**

- `self`
- `introspector`

##### feed_title

```python
def feed_title(self) -> str
```

Human-readable title extracted from the wrapped introspector.

**Parameters:**

- `self`

**Returns:** str

##### base_url

```python
def base_url(self) -> str
```

Root URL of the publisher from the wrapped introspector.

**Parameters:**

- `self`

**Returns:** str


### RssFeedIntrospectorFactory

Factory for creating RSS feed introspectors.

#### Methods

##### create

```python
def create(self, url: str) -> FeedIntrospector
```

Create an adapted RSS feed introspector for the given URL.

Instantiates ``RssFeedIntrospector`` and wraps it in
``RssFeedIntrospectorAdapter`` so it satisfies the
``FeedIntrospector`` protocol.

Args:
    url: RSS/Atom feed URL to introspect.

Returns:
    An ``RssFeedIntrospectorAdapter`` exposing ``feed_title``
    and ``base_url`` for the given feed.

**Parameters:**

- `self`
- `url` (str)

**Returns:** FeedIntrospector


### SourceConfigGeneratorAdapter

Adapter for existing SourceConfigGenerator.

#### Methods

##### __init__

```python
def __init__(self, generator_class)
```

Store the SourceConfigGenerator class for deferred instantiation.

Args:
    generator_class: The ``SourceConfigGenerator`` class (not an
        instance). It will be instantiated per call to
        ``generate_and_save`` with the serialized metadata dict.

**Parameters:**

- `self`
- `generator_class`

##### generate_and_save

```python
def generate_and_save(self, metadata: SourceMetadata, config_path: Path) -> Path
```

Serialize metadata and delegate to the wrapped generator class.

Converts ``SourceMetadata`` to the dict format expected by
``SourceConfigGenerator``, instantiates it, and calls its own
``generate_and_save`` method.

Args:
    metadata: Source metadata to serialize into a YAML config file.
    config_path: Directory where the config file should be written.

Returns:
    Path to the written YAML config file.

**Parameters:**

- `self`
- `metadata` (SourceMetadata)
- `config_path` (Path)

**Returns:** Path


### SubprocessSourceTester

Lightweight RSS connectivity tester with live progress display.

#### Methods

##### test_source

```python
def test_source(self, source_id: str, count: int = 1) -> bool
```

Test a source by fetching its RSS feed and counting articles.

Replaces the old subprocess approach: no full article download,
no output files created, no 60-second wait. Just an RSS HEAD +
GET + parse - typically completes in 2-5 seconds.

Shows the existing ProgressIndicator with live stage updates so
the user always knows what is happening.

Args:
    source_id: The source identifier to test.
    count: Unused (kept for interface compatibility).

Returns:
    ``True`` if the feed is reachable and contains at least one
    entry, ``False`` otherwise.

**Parameters:**

- `self`
- `source_id` (str)
- `count` (int) *optional*

**Returns:** bool

##### _get_rss_url

```python
def _get_rss_url(self, source_id: str) -> Optional[str]
```

Return the rss_url from the saved YAML for *source_id*, or None.

**Parameters:**

- `self`
- `source_id` (str)

**Returns:** Optional[str]


### RegistryCategoryProvider

Category provider using source registry.

#### Methods

##### get_available_categories

```python
def get_available_categories(self) -> List[str]
```

Return categories derived from all currently registered sources.

Queries the global ``SourceRegistry`` for all active source configs
and collects unique ``category`` values. Falls back to a hard-coded
default list if the registry is unavailable or yields no categories.

Returns:
    Sorted list of category strings (e.g. ``["ai", "news", "tech"]``).
    Defaults to ``['tech', 'news', 'science', 'ai', 'sports', 'general']``
    if the registry cannot be reached.

**Parameters:**

- `self`

**Returns:** List[str]


## Functions

### _stop_silent

```python
def _stop_silent()
```

Stop spinner and clear line without printing a summary.

