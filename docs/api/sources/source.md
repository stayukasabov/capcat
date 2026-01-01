# sources.specialized.youtube.source

**File:** `Application/sources/specialized/youtube/source.py`

## Description

YouTube specialized source implementation.
YouTube content is video-based and cannot be meaningfully archived as text,
so we create placeholder articles with links to original videos.

## Classes

### YouTubeSource

**Inherits from:** BaseSource

YouTube specialized source that creates placeholder articles.

#### Methods

##### source_type

```python
def source_type(self) -> str
```

**Parameters:**

- `self`

**Returns:** str

##### can_handle_url

```python
def can_handle_url(cls, url: str) -> bool
```

Check if this source can handle the given URL.

**Parameters:**

- `cls`
- `url` (str)

**Returns:** bool

##### discover_articles

```python
def discover_articles(self, count: int) -> List[Article]
```

YouTube discovery not supported without API access.

**Parameters:**

- `self`
- `count` (int)

**Returns:** List[Article]

##### _extract_video_title

```python
def _extract_video_title(self, url: str) -> Optional[str]
```

Extract video title from YouTube using yt-dlp.

Args:
    url: YouTube video URL

Returns:
    Video title or None if extraction fails

**Parameters:**

- `self`
- `url` (str)

**Returns:** Optional[str]

##### fetch_article_content

```python
def fetch_article_content(self, article: Article, output_dir: str, progress_callback = None) -> Tuple[bool, Optional[str]]
```

Create placeholder article with actual video title.

**Parameters:**

- `self`
- `article` (Article)
- `output_dir` (str)
- `progress_callback` *optional*

**Returns:** Tuple[bool, Optional[str]]


