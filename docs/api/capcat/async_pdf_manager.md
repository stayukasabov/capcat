# capcat.core.async_pdf_manager

**File:** `Application/capcat/core/async_pdf_manager.py`

## Description

Asynchronous PDF download manager to prevent thread pool exhaustion.
Handles PDF downloads separately from article processing.

## Classes

### AsyncPDFManager

Manages asynchronous PDF downloads to prevent blocking article processing threads.

Instead of downloading PDFs synchronously during article processing, this manager:
1. Collects PDF links during article processing
2. Downloads PDFs asynchronously in background
3. Updates markdown files once downloads complete

#### Methods

##### __init__

```python
def __init__(self, max_workers: int = 4, pdf_config: PdfConfig = None)
```

**Parameters:**

- `self`
- `max_workers` (int) *optional*
- `pdf_config` (PdfConfig) *optional*

##### start

```python
def start(self)
```

Start the background PDF download service.

**Parameters:**

- `self`

##### stop

```python
def stop(self)
```

Stop the background PDF download service.

**Parameters:**

- `self`

##### extract_and_queue_pdf_links

```python
def extract_and_queue_pdf_links(self, markdown_content: str, article_folder_path: str) -> Tuple[str, int]
```

Extract PDF links from markdown and queue them for async download.
Returns updated markdown with placeholder links and count of PDFs queued.

**Parameters:**

- `self`
- `markdown_content` (str)
- `article_folder_path` (str)

**Returns:** Tuple[str, int]

##### get_queued_urls_for_folder

```python
def get_queued_urls_for_folder(self, folder_path: str) -> List[str]
```

Return and remove the queued PDF URLs for a given article folder.

**Parameters:**

- `self`
- `folder_path` (str)

**Returns:** List[str]

##### update_article_with_completed_downloads

```python
def update_article_with_completed_downloads(self, markdown_file_path: str)
```

Update an article's markdown file with completed PDF downloads.
Replaces placeholder links in the body and adds paths to frontmatter.

**Parameters:**

- `self`
- `markdown_file_path` (str)

##### _worker_loop

```python
def _worker_loop(self)
```

Background worker loop for processing PDF download queue.

**Parameters:**

- `self`

##### _download_pdf

```python
def _download_pdf(self, download_info: dict)
```

Download a single PDF file.

**Parameters:**

- `self`
- `download_info` (dict)

##### wait_for_downloads

```python
def wait_for_downloads(self, urls: List[str], timeout: float = 30.0) -> bool
```

Wait for specific PDF downloads to complete.
Returns True if all completed, False if timeout.

**Parameters:**

- `self`
- `urls` (List[str])
- `timeout` (float) *optional*

**Returns:** bool

##### wait_until_idle

```python
def wait_until_idle(self, timeout: float = 60.0) -> bool
```

Block until the download queue is empty and no downloads are active.

Returns True if idle before timeout, False if timeout expired.
Used after all articles are processed to drain pending PDF downloads
before the batch command returns.

Logs an INFO progress message only when the download counts change,
so the terminal does not display repeated identical lines.

**Parameters:**

- `self`
- `timeout` (float) *optional*

**Returns:** bool

##### get_status

```python
def get_status(self) -> Dict
```

Get current status of the PDF download manager.

**Parameters:**

- `self`

**Returns:** Dict


## Functions

### pdf_exceeds_size_limit

```python
def pdf_exceeds_size_limit(url: str, session, max_bytes: int) -> bool
```

Return True if HEAD response reports Content-Length > max_bytes.

**Parameters:**

- `url` (str)
- `session`
- `max_bytes` (int)

**Returns:** bool

### initialize_pdf_manager

```python
def initialize_pdf_manager(pdf_config: 'PdfConfig') -> AsyncPDFManager
```

Return the running global AsyncPDFManager, creating and starting it if needed.

Idempotent: subsequent calls with any config return the already-running instance.
The manager is started on first creation; callers must not call .start() themselves.

**Parameters:**

- `pdf_config` ('PdfConfig')

**Returns:** AsyncPDFManager

### get_pdf_manager

```python
def get_pdf_manager() -> AsyncPDFManager
```

Get the global async PDF manager instance.

**Returns:** AsyncPDFManager

### shutdown_pdf_manager

```python
def shutdown_pdf_manager()
```

Shutdown the global PDF manager.

### is_pdf_url

```python
def is_pdf_url(url: str) -> bool
```

**Parameters:**

- `url` (str)

**Returns:** bool

### replace_link

```python
def replace_link(match)
```

**Parameters:**

- `match`

### replace_placeholder

```python
def replace_placeholder(match)
```

**Parameters:**

- `match`

