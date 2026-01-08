# scripts.generate_diagrams

**File:** `Application/scripts/generate_diagrams.py`

## Description

Generate Architecture Diagrams for Capcat

Creates Mermaid diagrams for system architecture, data flow, and component relationships.

## Classes

### DiagramGenerator

Generates various architectural diagrams.

#### Methods

##### __init__

```python
def __init__(self, output_dir)
```

**Parameters:**

- `self`
- `output_dir`

##### generate_all_diagrams

```python
def generate_all_diagrams(self) -> None
```

Generate all architecture diagrams.

**Parameters:**

- `self`

**Returns:** None

##### generate_system_architecture

```python
def generate_system_architecture(self) -> None
```

Generate overall system architecture diagram.

**Parameters:**

- `self`

**Returns:** None

##### generate_data_flow

```python
def generate_data_flow(self) -> None
```

Generate data flow diagram.

**Parameters:**

- `self`

**Returns:** None

##### generate_source_system

```python
def generate_source_system(self) -> None
```

Generate source system architecture diagram.

**Parameters:**

- `self`

**Returns:** None

##### generate_processing_pipeline

```python
def generate_processing_pipeline(self) -> None
```

Generate processing pipeline diagram.

**Parameters:**

- `self`

**Returns:** None

##### generate_deployment_diagram

```python
def generate_deployment_diagram(self) -> None
```

Generate deployment architecture diagram.

**Parameters:**

- `self`

**Returns:** None

##### generate_class_diagrams

```python
def generate_class_diagrams(self) -> None
```

Generate class diagrams for key components.

**Parameters:**

- `self`

**Returns:** None


## Functions

### main

```python
def main()
```

Main diagram generation function.

