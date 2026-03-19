# capcat.core.storage_manager

**File:** `Application/capcat/core/storage_manager.py`

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
def save_article_content(self, article_folder_path: str, content: str, title: str) -> str
```

Save article content to the article folder.

Args:
    article_folder_path: Path to the article folder
    content: Content to save
    title: Article title used to generate the markdown filename

Returns:
    Path to the saved content file

**Parameters:**

- `self`
- `article_folder_path` (str)
- `content` (str)
- `title` (str)

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


## Functions

### article_md_filename

```python
def article_md_filename(title: str) -> str
```

Return sanitized markdown filename for an article (e.g. 'My-Title.md').

The base stem is truncated at 200 chars before adding the extension.
Spaces are replaced with hyphens.

**Parameters:**

- `title` (str)

**Returns:** str

### comments_md_filename

```python
def comments_md_filename(title: str) -> str
```

Return sanitized markdown filename for comments (e.g. 'My-Title-Comments.md').

The base stem is truncated at 200 chars; '-Comments.md' is appended after truncation.
Spaces are replaced with hyphens.

**Parameters:**

- `title` (str)

**Returns:** str

### find_article_md

```python
def find_article_md(folder: Path) -> 'Path | None'
```

Return the article markdown path in folder, or None if absent.

Non-recursive: only searches direct children of folder.
Returns the first .md file whose stem does not end in '-Comments'.

**Parameters:**

- `folder` (Path)

**Returns:** 'Path | None'

### find_comments_md

```python
def find_comments_md(folder: Path) -> 'Path | None'
```

Return the comments markdown path in folder, or None if absent.

**Parameters:**

- `folder` (Path)

**Returns:** 'Path | None'

### inject_comments_wikilink

```python
def inject_comments_wikilink(article_folder_path: str, comments_stem: str) -> bool
```

Inject a → [[comments_stem|Comments]] wikilink at top and bottom of the article .md.

Idempotent: if line 1 already starts with '→ [[', returns True without modifying.
Returns False on any error without raising.
Module-level function, not a StorageManager method.

**Parameters:**

- `article_folder_path` (str)
- `comments_stem` (str)

**Returns:** bool

