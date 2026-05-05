---
layout: default
render_with_liquid: false
---

# debug.fix-sources

**File:** `Application/debug/fix-sources.py`

## Description

Source Fix Tool
Automatically suggests and applies fixes for problematic sources.

## Classes

### SourceFixer

#### Methods

##### __init__

```python
def __init__(self, capcat_root = '/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application')
```

**Parameters:**

- `self`
- `capcat_root` *optional*

##### fix_percepta_ai

```python
def fix_percepta_ai(self)
```

Fix percepta.ai source configuration.

**Parameters:**

- `self`

##### fix_ahwoo_com

```python
def fix_ahwoo_com(self)
```

Fix ahwoo.com source configuration.

**Parameters:**

- `self`

##### suggest_forbes_workaround

```python
def suggest_forbes_workaround(self)
```

Suggest workarounds for Forbes bot protection.

**Parameters:**

- `self`

##### apply_fixes

```python
def apply_fixes(self)
```

Apply all fixes for the problematic sources.

**Parameters:**

- `self`


## Functions

### main

```python
def main()
```

