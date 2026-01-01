# core.enhanced_argparse

**File:** `Application/core/enhanced_argparse.py`

## Description

Enhanced ArgumentParser with better error messages and validation.

## Classes

### EnhancedArgumentParser

**Inherits from:** argparse.ArgumentParser

Enhanced ArgumentParser with improved error messages and validation.

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### parse_args

```python
def parse_args(self, args: Optional[List[str]] = None, namespace = None)
```

Enhanced parse_args with better error handling.

**Parameters:**

- `self`
- `args` (Optional[List[str]]) *optional*
- `namespace` *optional*

##### _handle_flag_mistakes

```python
def _handle_flag_mistakes(self, args: List[str])
```

Handle common flag mistakes that trigger help.

**Parameters:**

- `self`
- `args` (List[str])

##### _handle_parsing_error

```python
def _handle_parsing_error(self, args: List[str], error: SystemExit)
```

Handle parsing errors with enhanced messages.

**Parameters:**

- `self`
- `args` (List[str])
- `error` (SystemExit)

##### error

```python
def error(self, message)
```

Override error method to provide enhanced error messages.

**Parameters:**

- `self`
- `message`


## Functions

### create_enhanced_parser

```python
def create_enhanced_parser() -> EnhancedArgumentParser
```

Create an enhanced argument parser with better error messages.

**Returns:** EnhancedArgumentParser

