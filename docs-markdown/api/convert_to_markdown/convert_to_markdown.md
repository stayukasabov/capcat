# convert_to_markdown

**File:** `Application/convert_to_markdown.py`

## Classes

### HTMLToMarkdownConverter

**Inherits from:** HTMLParser

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### handle_starttag

```python
def handle_starttag(self, tag, attrs)
```

**Parameters:**

- `self`
- `tag`
- `attrs`

⚠️ **High complexity:** 20

##### handle_endtag

```python
def handle_endtag(self, tag)
```

**Parameters:**

- `self`
- `tag`

⚠️ **High complexity:** 23

##### handle_data

```python
def handle_data(self, data)
```

**Parameters:**

- `self`
- `data`

##### get_markdown

```python
def get_markdown(self)
```

**Parameters:**

- `self`


## Functions

### create_mermaid_diagram

```python
def create_mermaid_diagram(image_context, index)
```

Create a mermaid diagram based on image context

**Parameters:**

- `image_context`
- `index`

⚠️ **High complexity:** 16

### main

```python
def main()
```

