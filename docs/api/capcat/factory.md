---
layout: default
render_with_liquid: false
---

# capcat.htmlgen.factory

**File:** `Application/capcat/htmlgen/factory.py`

## Description

Factory for creating ArticleHTMLGenerator instances.

## Classes

### HTMLGeneratorFactory

Construction point for HTML generators.

Minimal now. Registry pattern for source-specific subclasses
added when the first source requires custom HTML logic.

#### Methods

##### create

```python
def create() -> ArticleHTMLGenerator
```

Return a new ArticleHTMLGenerator instance.

**Returns:** ArticleHTMLGenerator


