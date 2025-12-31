# fix_sources_in_docs

**File:** `Application/fix_sources_in_docs.py`

## Description

Fix hardcoded outdated sources in documentation.

## Constants

### REAL_SOURCES

**Value:** `{'tech': 'ieee, mashable', 'techpro': 'hn, lb, iq', 'news': 'bbc, guardian', 'science': 'nature, scientificamerican', 'ai': 'mitnews', 'sports': 'bbcsport'}`

### FAKE_SOURCES

**Value:** `['gizmodo', 'futurism', 'lesswrong', 'googleai', 'openai', 'cnn']`

## Functions

### fix_file

```python
def fix_file(filepath)
```

Fix source mentions in a file.

**Parameters:**

- `filepath`

