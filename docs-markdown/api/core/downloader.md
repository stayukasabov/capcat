# core.downloader

**File:** `Application/core/downloader.py`

## Description

Media downloader for Capcat.
Handles downloading of images, documents, audio, and video files.

## Functions

### is_document_url

```python
def is_document_url(url: str) -> bool
```

Check if a URL points to a document file using file extension only (fast).

**Parameters:**

- `url` (str)

**Returns:** bool

### is_audio_url

```python
def is_audio_url(url: str) -> bool
```

Check if a URL points to an audio file using file extension only (fast).

**Parameters:**

- `url` (str)

**Returns:** bool

### is_video_url

```python
def is_video_url(url: str) -> bool
```

Check if a URL points to a video file using file extension only (fast).

**Parameters:**

- `url` (str)

**Returns:** bool

### is_image_url

```python
def is_image_url(url: str) -> bool
```

Check if a URL points to an image file using file extension only (fast).

**Parameters:**

- `url` (str)

**Returns:** bool

### download_file

```python
def download_file(file_url: str, folder_path: str, file_type: str, media_enabled: bool = False) -> Optional[str]
```

Download a file (image, document, audio, or video) and save it to the appropriate folder.

Args:
    file_url: URL of the file to download
    folder_path: Path to the article folder
    file_type: Type of file ('image', 'audio', 'video', 'document')
    media_enabled: Whether --media flag is enabled (affects size limits)

**Parameters:**

- `file_url` (str)
- `folder_path` (str)
- `file_type` (str)
- `media_enabled` (bool) *optional*

**Returns:** Optional[str]

⚠️ **High complexity:** 68

