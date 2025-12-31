# scripts.generate_source_config

**File:** `Application/scripts/generate_source_config.py`

## Description

Interactive script to generate comprehensive YAML configuration files
for config-driven sources in Capcat.

This script creates production-ready configs with all necessary fields
including discovery methods, selectors, image processing, and templates.

## Functions

### prompt_text

```python
def prompt_text(question: str, default: Optional[str] = None) -> str
```

Prompt user for text input with optional default value.

Args:
    question: Question to ask the user
    default: Optional default value

Returns:
    User input or default value

**Parameters:**

- `question` (str)
- `default` (Optional[str]) *optional*

**Returns:** str

### prompt_yes_no

```python
def prompt_yes_no(question: str, default: bool = False) -> bool
```

Prompt user for yes/no question.

Args:
    question: Question to ask
    default: Default value if user just presses enter

Returns:
    True for yes, False for no

**Parameters:**

- `question` (str)
- `default` (bool) *optional*

**Returns:** bool

### prompt_list

```python
def prompt_list(question: str, examples: List[str]) -> List[str]
```

Prompt user for a list of items.

Args:
    question: Question to ask
    examples: Example values to show

Returns:
    List of user-provided items

**Parameters:**

- `question` (str)
- `examples` (List[str])

**Returns:** List[str]

### prompt_choice

```python
def prompt_choice(question: str, choices: List[str], default: str) -> str
```

Prompt user to choose from a list of options.

Args:
    question: Question to ask
    choices: List of valid choices
    default: Default choice

Returns:
    Selected choice

**Parameters:**

- `question` (str)
- `choices` (List[str])
- `default` (str)

**Returns:** str

### generate_config

```python
def generate_config() -> Dict
```

Interactively gather configuration data from user.

Returns:
    Dictionary containing the complete configuration

**Returns:** Dict

### save_config

```python
def save_config(config: Dict, output_path: Optional[Path] = None) -> Path
```

Save configuration to YAML file.

Args:
    config: Configuration dictionary
    output_path: Optional custom output path

Returns:
    Path to saved file

**Parameters:**

- `config` (Dict)
- `output_path` (Optional[Path]) *optional*

**Returns:** Path

### parse_args

```python
def parse_args()
```

Parse command-line arguments.

### main

```python
def main()
```

Main entry point for the config generator.

