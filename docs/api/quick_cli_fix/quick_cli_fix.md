# quick_cli_fix

**File:** `Application/quick_cli_fix.py`

## Description

Quick CLI validation fix to catch common flag mistakes.
This can be imported and used before argparse to fix obvious errors.

## Functions

### preprocess_cli_args

```python
def preprocess_cli_args(args: List[str]) -> Tuple[List[str], List[str]]
```

Preprocess CLI arguments to fix common mistakes and provide warnings.

Args:
    args: Raw command line arguments

Returns:
    Tuple of (corrected_args, warnings)

**Parameters:**

- `args` (List[str])

**Returns:** Tuple[List[str], List[str]]

### validate_and_fix_command

```python
def validate_and_fix_command() -> List[str]
```

Validate and fix command line arguments before main processing.

Returns:
    Corrected command line arguments

**Returns:** List[str]

### detect_help_from_typo

```python
def detect_help_from_typo(args: List[str]) -> bool
```

Detect if help was likely triggered by a typo rather than intentional.

Args:
    args: Command line arguments

Returns:
    True if help was likely triggered by typo

**Parameters:**

- `args` (List[str])

**Returns:** bool

