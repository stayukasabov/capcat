---
layout: default
render_with_liquid: false
---

# debug.source-tester

**File:** `Application/debug/source-tester.py`

## Description

Source Configuration Tester
Tests Capcat source configurations and suggests fixes.

## Classes

### SourceTester

#### Methods

##### __init__

```python
def __init__(self, capcat_root = '/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application')
```

**Parameters:**

- `self`
- `capcat_root` *optional*

##### test_source

```python
def test_source(self, source_id)
```

Test a specific source configuration.

**Parameters:**

- `self`
- `source_id`

##### find_source_config

```python
def find_source_config(self, source_id)
```

Find config file for a source.

**Parameters:**

- `self`
- `source_id`

##### test_rss_discovery

```python
def test_rss_discovery(self, config)
```

Test RSS feed discovery.

**Parameters:**

- `self`
- `config`

##### test_article_extraction

```python
def test_article_extraction(self, config)
```

Test article extraction on a sample article.

**Parameters:**

- `self`
- `config`

##### get_sample_article_url

```python
def get_sample_article_url(self, config)
```

Get a sample article URL for testing.

**Parameters:**

- `self`
- `config`

##### suggest_title_selectors

```python
def suggest_title_selectors(self, soup)
```

Suggest alternative title selectors.

**Parameters:**

- `self`
- `soup`

##### suggest_content_selectors

```python
def suggest_content_selectors(self, soup)
```

Suggest alternative content selectors.

**Parameters:**

- `self`
- `soup`

##### test_all_sources

```python
def test_all_sources(self)
```

Test all configured sources.

**Parameters:**

- `self`


## Functions

### main

```python
def main()
```

⚠️ **High complexity:** 11

