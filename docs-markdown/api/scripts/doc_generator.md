# scripts.doc_generator

**File:** `Application/scripts/doc_generator.py`

## Description

Documentation Generator for Capcat

Automatically extracts and generates comprehensive documentation from the codebase.

## Classes

### FunctionDoc

Documentation for a function.


### ClassDoc

Documentation for a class.


### ModuleDoc

Documentation for a module.


### CodeAnalyzer

Analyzes Python code to extract documentation information.

#### Methods

##### __init__

```python
def __init__(self, project_root: str)
```

**Parameters:**

- `self`
- `project_root` (str)

##### analyze_project

```python
def analyze_project(self) -> None
```

Analyze the entire project structure.

**Parameters:**

- `self`

**Returns:** None

##### _analyze_file

```python
def _analyze_file(self, file_path: Path) -> None
```

Analyze a single Python file.

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** None

##### _get_module_name

```python
def _get_module_name(self, file_path: Path) -> str
```

Get the module name from file path.

**Parameters:**

- `self`
- `file_path` (Path)

**Returns:** str

##### _extract_imports

```python
def _extract_imports(self, tree: ast.AST) -> List[str]
```

Extract import statements.

**Parameters:**

- `self`
- `tree` (ast.AST)

**Returns:** List[str]

##### _extract_constants

```python
def _extract_constants(self, tree: ast.AST) -> List[Dict[str, Any]]
```

Extract module-level constants.

**Parameters:**

- `self`
- `tree` (ast.AST)

**Returns:** List[Dict[str, Any]]

##### _is_method

```python
def _is_method(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool
```

Check if a function is a method of a class.

**Parameters:**

- `self`
- `func_node` (ast.FunctionDef)
- `tree` (ast.AST)

**Returns:** bool

##### _analyze_function

```python
def _analyze_function(self, node: ast.FunctionDef, module_name: str, file_path: Path) -> FunctionDoc
```

Analyze a function definition.

**Parameters:**

- `self`
- `node` (ast.FunctionDef)
- `module_name` (str)
- `file_path` (Path)

**Returns:** FunctionDoc

##### _analyze_class

```python
def _analyze_class(self, node: ast.ClassDef, module_name: str, file_path: Path, content: str) -> ClassDoc
```

Analyze a class definition.

**Parameters:**

- `self`
- `node` (ast.ClassDef)
- `module_name` (str)
- `file_path` (Path)
- `content` (str)

**Returns:** ClassDoc

##### _extract_parameters

```python
def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]
```

Extract function parameters.

**Parameters:**

- `self`
- `node` (ast.FunctionDef)

**Returns:** List[Dict[str, Any]]

##### _extract_return_type

```python
def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]
```

Extract function return type.

**Parameters:**

- `self`
- `node` (ast.FunctionDef)

**Returns:** Optional[str]

##### _extract_decorators

```python
def _extract_decorators(self, node: ast.FunctionDef) -> List[str]
```

Extract function decorators.

**Parameters:**

- `self`
- `node` (ast.FunctionDef)

**Returns:** List[str]

##### _extract_class_attributes

```python
def _extract_class_attributes(self, node: ast.ClassDef) -> List[Dict[str, Any]]
```

Extract class attributes.

**Parameters:**

- `self`
- `node` (ast.ClassDef)

**Returns:** List[Dict[str, Any]]

##### _extract_inheritance

```python
def _extract_inheritance(self, node: ast.ClassDef) -> List[str]
```

Extract class inheritance.

**Parameters:**

- `self`
- `node` (ast.ClassDef)

**Returns:** List[str]

##### _calculate_complexity

```python
def _calculate_complexity(self, node: ast.FunctionDef) -> int
```

Calculate cyclomatic complexity.

**Parameters:**

- `self`
- `node` (ast.FunctionDef)

**Returns:** int


### DocumentationGenerator

Generates various types of documentation.

#### Methods

##### __init__

```python
def __init__(self, analyzer: CodeAnalyzer, output_dir: str)
```

**Parameters:**

- `self`
- `analyzer` (CodeAnalyzer)
- `output_dir` (str)

##### generate_all_docs

```python
def generate_all_docs(self) -> None
```

Generate all documentation types.

**Parameters:**

- `self`

**Returns:** None

##### generate_api_docs

```python
def generate_api_docs(self) -> None
```

Generate API documentation in markdown format.

**Parameters:**

- `self`

**Returns:** None

##### _generate_package_docs

```python
def _generate_package_docs(self, package_name: str, modules: List[ModuleDoc], api_dir: Path) -> None
```

Generate documentation for a package.

**Parameters:**

- `self`
- `package_name` (str)
- `modules` (List[ModuleDoc])
- `api_dir` (Path)

**Returns:** None

##### _generate_module_docs

```python
def _generate_module_docs(self, module: ModuleDoc, package_dir: Path) -> None
```

Generate documentation for a single module.

**Parameters:**

- `self`
- `module` (ModuleDoc)
- `package_dir` (Path)

**Returns:** None

##### _format_class_docs

```python
def _format_class_docs(self, cls: ClassDoc) -> str
```

Format class documentation.

**Parameters:**

- `self`
- `cls` (ClassDoc)

**Returns:** str

##### _format_function_docs

```python
def _format_function_docs(self, func: FunctionDoc, is_method: bool = False) -> str
```

Format function documentation.

**Parameters:**

- `self`
- `func` (FunctionDoc)
- `is_method` (bool) *optional*

**Returns:** str

⚠️ **High complexity:** 13

##### _generate_api_index

```python
def _generate_api_index(self, packages: Dict[str, List[ModuleDoc]], api_dir: Path) -> None
```

Generate API documentation index.

**Parameters:**

- `self`
- `packages` (Dict[str, List[ModuleDoc]])
- `api_dir` (Path)

**Returns:** None

##### generate_architecture_docs

```python
def generate_architecture_docs(self) -> None
```

Generate architecture documentation with diagrams.

**Parameters:**

- `self`

**Returns:** None

##### _generate_component_docs

```python
def _generate_component_docs(self, arch_dir: Path) -> None
```

Generate detailed component documentation.

**Parameters:**

- `self`
- `arch_dir` (Path)

**Returns:** None

##### generate_module_reference

```python
def generate_module_reference(self) -> None
```

Generate complete module reference.

**Parameters:**

- `self`

**Returns:** None

##### generate_developer_guide

```python
def generate_developer_guide(self) -> None
```

Generate developer guide.

**Parameters:**

- `self`

**Returns:** None

##### generate_readme

```python
def generate_readme(self) -> None
```

Generate comprehensive README.

**Parameters:**

- `self`

**Returns:** None

##### generate_index

```python
def generate_index(self) -> None
```

Generate documentation index.

**Parameters:**

- `self`

**Returns:** None


## Functions

### main

```python
def main()
```

Main documentation generation function.

