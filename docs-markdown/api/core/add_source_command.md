# core.source_system.add_source_command

**File:** `Application/core/source_system/add_source_command.py`

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

#### Methods

##### feed_title

```python
def feed_title(self) -> str
```

**Parameters:**

- `self`

**Returns:** str

##### base_url

```python
def base_url(self) -> str
```

**Parameters:**

- `self`

**Returns:** str


### UserInterface

**Inherits from:** Protocol

Protocol for user interaction.

#### Methods

##### get_source_id

```python
def get_source_id(self, suggested: str) -> str
```

**Parameters:**

- `self`
- `suggested` (str)

**Returns:** str

##### select_category

```python
def select_category(self, categories: List[str]) -> str
```

**Parameters:**

- `self`
- `categories` (List[str])

**Returns:** str

##### confirm_bundle_addition

```python
def confirm_bundle_addition(self) -> bool
```

**Parameters:**

- `self`

**Returns:** bool

##### select_bundle

```python
def select_bundle(self, bundles: List[str]) -> Optional[str]
```

**Parameters:**

- `self`
- `bundles` (List[str])

**Returns:** Optional[str]

##### confirm_test_fetch

```python
def confirm_test_fetch(self) -> bool
```

**Parameters:**

- `self`

**Returns:** bool

##### show_success

```python
def show_success(self, message: str) -> None
```

**Parameters:**

- `self`
- `message` (str)

**Returns:** None

##### show_error

```python
def show_error(self, message: str) -> None
```

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

**Parameters:**

- `self`

**Returns:** List[str]

##### add_source_to_bundle

```python
def add_source_to_bundle(self, source_id: str, bundle_name: str) -> None
```

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
def __init__(self, introspector_factory: 'IntrospectorFactory', ui: UserInterface, config_generator: ConfigGenerator, bundle_manager: BundleManager, source_tester: SourceTester, category_provider: CategoryProvider, config_path: Path, bundles_path: Path, logger: Optional[Any] = None)
```

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

##### execute

```python
def execute(self, url: str) -> None
```

Execute the add-source command.

Args:
    url: RSS feed URL to add

Raises:
    CapcatError: If any step in the process fails

**Parameters:**

- `self`
- `url` (str)

**Returns:** None

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

**Parameters:**

- `self`
- `introspector`

##### feed_title

```python
def feed_title(self) -> str
```

**Parameters:**

- `self`

**Returns:** str

##### base_url

```python
def base_url(self) -> str
```

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

**Parameters:**

- `self`
- `generator_class`

##### generate_and_save

```python
def generate_and_save(self, metadata: SourceMetadata, config_path: Path) -> Path
```

**Parameters:**

- `self`
- `metadata` (SourceMetadata)
- `config_path` (Path)

**Returns:** Path


### SubprocessSourceTester

Source tester using subprocess calls.

#### Methods

##### test_source

```python
def test_source(self, source_id: str, count: int = 1) -> bool
```

**Parameters:**

- `self`
- `source_id` (str)
- `count` (int) *optional*

**Returns:** bool


### RegistryCategoryProvider

Category provider using source registry.

#### Methods

##### get_available_categories

```python
def get_available_categories(self) -> List[str]
```

**Parameters:**

- `self`

**Returns:** List[str]


