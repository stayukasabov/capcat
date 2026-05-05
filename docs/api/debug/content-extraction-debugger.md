---
layout: default
render_with_liquid: false
---

# debug.content-extraction-debugger

**File:** `Application/debug/content-extraction-debugger.py`

## Description

Content Extraction Debugging Tool for Capcat
Helps diagnose why articles return empty markdown or fail to fetch.

## Classes

### ContentExtractionDebugger

#### Methods

##### __init__

```python
def __init__(self, capcat_root = '/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application')
```

**Parameters:**

- `self`
- `capcat_root` *optional*

##### setup_session

```python
def setup_session(self)
```

Setup session with realistic headers.

**Parameters:**

- `self`

##### debug_url

```python
def debug_url(self, url)
```

Debug content extraction for a specific URL.

**Parameters:**

- `self`
- `url`

##### test_connectivity

```python
def test_connectivity(self, url)
```

Test basic connectivity to the URL.

**Parameters:**

- `self`
- `url`

##### find_source_config

```python
def find_source_config(self, url)
```

Find the source configuration for this URL.

**Parameters:**

- `self`
- `url`

##### fetch_raw_html

```python
def fetch_raw_html(self, url)
```

Fetch raw HTML content.

**Parameters:**

- `self`
- `url`

##### analyze_html_structure

```python
def analyze_html_structure(self, html_content, url)
```

Analyze HTML structure for common content patterns.

**Parameters:**

- `self`
- `html_content`
- `url`

##### test_extraction_patterns

```python
def test_extraction_patterns(self, html_content, config_file, url)
```

Test extraction patterns from source config.

**Parameters:**

- `self`
- `html_content`
- `config_file`
- `url`

##### check_anti_bot_protection

```python
def check_anti_bot_protection(self, html_content, url)
```

Check for anti-bot protection indicators.

**Parameters:**

- `self`
- `html_content`
- `url`


## Functions

### main

```python
def main()
```

