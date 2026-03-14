# capcat.commands.fetch

**File:** `Application/capcat/commands/fetch.py`

## Description

Batch fetch command — processes multiple sources via the unified processor.

## Functions

### process_sources

```python
def process_sources(sources: List[str], args: argparse.Namespace, config: object, logger: object, generate_html: bool = False, output_dir: str = '.') -> Dict[str, object]
```

Process multiple sources using the unified processor.

Args:
    sources: List of source identifiers to process (e.g., 'hn', 'bbc').
    args: Parsed arguments with count, quiet, verbose, media attributes.
    config: Configuration object with system settings.
    logger: Logger instance for output.
    generate_html: Whether to generate HTML output after processing.
    output_dir: Output directory path for saved articles.

Returns:
    Dict with keys 'successful' (list), 'failed' (list of tuples), 'total'.

**Parameters:**

- `sources` (List[str])
- `args` (argparse.Namespace)
- `config` (object)
- `logger` (object)
- `generate_html` (bool) *optional*
- `output_dir` (str) *optional*

**Returns:** Dict[str, object]

