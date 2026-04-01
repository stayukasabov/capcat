# analyze_hn_pdf_patterns

**File:** `Application/analyze_hn_pdf_patterns.py`

## Description

Analyze HN articles to understand PDF link patterns without downloading.
This will show us how many PDFs per article we're dealing with.

## Functions

### is_pdf_url_broad

```python
def is_pdf_url_broad(url: str) -> bool
```

Broad PDF detection (same as _download_pdf_links_from_markdown).

**Parameters:**

- `url` (str)

**Returns:** bool

### is_pdf_url_strict

```python
def is_pdf_url_strict(url: str) -> bool
```

Strict PDF detection (only .pdf extension).

**Parameters:**

- `url` (str)

**Returns:** bool

### analyze_article_pdfs

```python
def analyze_article_pdfs(url: str, title: str, session: requests.Session) -> dict
```

Analyze a single article for PDF links.

**Parameters:**

- `url` (str)
- `title` (str)
- `session` (requests.Session)

**Returns:** dict

⚠️ **High complexity:** 13

### analyze_hn_pdf_patterns

```python
def analyze_hn_pdf_patterns()
```

Analyze PDF patterns in HN articles.

