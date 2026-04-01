# analyze_hn_pdfs_simple

**File:** `Application/analyze_hn_pdfs_simple.py`

## Description

Simple analysis of PDF links in HN articles using direct API approach.

## Functions

### is_pdf_url_broad

```python
def is_pdf_url_broad(url: str) -> bool
```

Broad PDF detection (same as capcat uses).

**Parameters:**

- `url` (str)

**Returns:** bool

### get_hn_articles

```python
def get_hn_articles(limit = 10)
```

Get HN front page articles.

**Parameters:**

- `limit` *optional*

### analyze_article_pdfs

```python
def analyze_article_pdfs(article)
```

Analyze PDF links in a single article.

**Parameters:**

- `article`

⚠️ **High complexity:** 12

### main

```python
def main()
```

