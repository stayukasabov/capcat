# debug_pdf_stalling

**File:** `Application/debug_pdf_stalling.py`

## Description

Diagnostic script to analyze PDF download stalling in HN source.
Adds instrumentation to understand thread pool usage and PDF download patterns.

## Classes

### DebugThreadMonitor

Monitor thread pool usage and PDF download patterns.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### track_thread_start

```python
def track_thread_start(self, thread_id, article_title)
```

**Parameters:**

- `self`
- `thread_id`
- `article_title`

##### track_thread_end

```python
def track_thread_end(self, thread_id, success)
```

**Parameters:**

- `self`
- `thread_id`
- `success`

##### track_pdf_start

```python
def track_pdf_start(self, thread_id, pdf_url)
```

**Parameters:**

- `self`
- `thread_id`
- `pdf_url`

##### track_pdf_end

```python
def track_pdf_end(self, thread_id, pdf_url, success)
```

**Parameters:**

- `self`
- `thread_id`
- `pdf_url`
- `success`

##### show_active_threads

```python
def show_active_threads(self)
```

**Parameters:**

- `self`


## Functions

### patch_article_fetcher

```python
def patch_article_fetcher()
```

Patch article fetcher to add monitoring.

### debug_hn_pdf_downloads

```python
def debug_hn_pdf_downloads()
```

Run HN with PDF downloads and monitor thread usage.

### monitored_download_pdf_links

```python
def monitored_download_pdf_links(self, markdown_content, article_folder_path)
```

**Parameters:**

- `self`
- `markdown_content`
- `article_folder_path`

### monitored_process_single

```python
def monitored_process_single(self, source, article, base_dir, download_files, progress_tracker, index)
```

**Parameters:**

- `self`
- `source`
- `article`
- `base_dir`
- `download_files`
- `progress_tracker`
- `index`

### monitor_loop

```python
def monitor_loop()
```

### is_pdf_url

```python
def is_pdf_url(u: str) -> bool
```

**Parameters:**

- `u` (str)

**Returns:** bool

### monitored_download_file

```python
def monitored_download_file(file_url, folder_path, file_type, media_enabled)
```

**Parameters:**

- `file_url`
- `folder_path`
- `file_type`
- `media_enabled`

