# debug.log-analyzer

**File:** `Application/debug/log-analyzer.py`

## Description

Capcat Log Analyzer
Analyzes Capcat logs to identify patterns in failures and warnings.

## Classes

### CapcatLogAnalyzer

#### Methods

##### __init__

```python
def __init__(self)
```

**Parameters:**

- `self`

##### analyze_log_file

```python
def analyze_log_file(self, log_file)
```

Analyze a log file for patterns.

**Parameters:**

- `self`
- `log_file`

##### analyze_log_content

```python
def analyze_log_content(self, content)
```

Analyze log content for patterns.

**Parameters:**

- `self`
- `content`

⚠️ **High complexity:** 11

##### print_analysis_report

```python
def print_analysis_report(self, results)
```

Print a comprehensive analysis report.

**Parameters:**

- `self`
- `results`

##### analyze_empty_markdown_pattern

```python
def analyze_empty_markdown_pattern(self, matches)
```

Analyze empty markdown patterns.

**Parameters:**

- `self`
- `matches`

##### analyze_access_forbidden_pattern

```python
def analyze_access_forbidden_pattern(self, matches)
```

Analyze access forbidden patterns.

**Parameters:**

- `self`
- `matches`

##### analyze_recent_logs

```python
def analyze_recent_logs(self)
```

Analyze recent Capcat execution logs.

**Parameters:**

- `self`

##### analyze_from_input

```python
def analyze_from_input(self, log_input)
```

Analyze log content from various inputs.

**Parameters:**

- `self`
- `log_input`

##### generate_recommendations

```python
def generate_recommendations(self, results)
```

Generate recommendations based on analysis.

**Parameters:**

- `self`
- `results`


## Functions

### main

```python
def main()
```

