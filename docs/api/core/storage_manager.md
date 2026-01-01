# core.storage_manager

**File:** `Application/core/storage_manager.py`

## Description

Storage management component for Capcat.

Handles file system operations, folder creation, and content storage
independently from the main article fetching logic.

## Classes

### StorageManager

Manages all file system operations for article storage.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### create_article_folder

```python
def create_article_folder(self, base_folder: str, title: str) -> str
```

Create a folder for storing an article's content.

Args:
    base_folder: Base directory to create the article folder in
    title: Article title to use for folder name
    
Returns:
    Path to the created article folder

**Parameters:**

- `self`
- `base_folder` (str)
- `title` (str)

**Returns:** str

##### save_article_content

```python
def save_article_content(self, article_folder_path: str, content: str) -> str
```

Save article content to the article folder.

Args:
    article_folder_path: Path to the article folder
    content: Content to save
    
Returns:
    Path to the saved content file

**Parameters:**

- `self`
- `article_folder_path` (str)
- `content` (str)

**Returns:** str

##### cleanup_empty_images_folder

```python
def cleanup_empty_images_folder(self, article_folder_path: str) -> None
```

Remove images folder if it exists but is empty.

Args:
    article_folder_path: Path to the article folder

**Parameters:**

- `self`
- `article_folder_path` (str)

**Returns:** None

##### _get_unique_folder_name

```python
def _get_unique_folder_name(self, base_folder: str, base_title: str) -> str
```

Get folder name - always returns base_title to allow overwrite.
When user runs repeatedly, content is replaced instead of creating duplicates.

**Parameters:**

- `self`
- `base_folder` (str)
- `base_title` (str)

**Returns:** str


