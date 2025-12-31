# Dependencies Documentation

## Overview

Capcat requires specific Python packages and system dependencies to function correctly. This document outlines all dependencies, installation procedures, and troubleshooting information.

## Python Version Requirements

- **Minimum**: Python 3.8+
- **Recommended**: Python 3.11+
- **Tested**: Python 3.9, 3.13

## Core Dependencies

All Python dependencies are specified in `requirements.txt` and automatically installed by the wrapper system.

### Required Packages

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Package</th>
      <th>Version</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>requests</code></td>
      <td>Latest</td>
      <td>HTTP requests and session management</td>
    </tr>
    <tr>
      <td><code>beautifulsoup4</code></td>
      <td>Latest</td>
      <td>HTML parsing and content extraction</td>
    </tr>
    <tr>
      <td><code>PyYAML</code></td>
      <td>Latest</td>
      <td>Configuration file parsing</td>
    </tr>
    <tr>
      <td><code>markdownify</code></td>
      <td>Latest</td>
      <td>HTML to Markdown conversion</td>
    </tr>
    <tr>
      <td><code>markdown</code></td>
      <td>>=3.5.0</td>
      <td>Markdown processing for HTML generation</td>
    </tr>
    <tr>
      <td><code>pygments</code></td>
      <td>>=2.16.0</td>
      <td>Syntax highlighting for code blocks</td>
    </tr>
  </tbody>
</table>
</div>

### Optional Dependencies

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Package</th>
      <th>Purpose</th>
      <th>Installation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>pymdownx</code></td>
      <td>Enhanced markdown extensions</td>
      <td><code>pip install pymdownx-extensions</code></td>
    </tr>
    <tr>
      <td><code>jinja2</code></td>
      <td>Advanced templating (fallback available)</td>
      <td><code>pip install jinja2</code></td>
    </tr>
  </tbody>
</table>
</div>

## Installation Methods

### Automatic Installation (Recommended)

The new wrapper system handles all dependency management automatically:

```bash
# Simply run capcat - dependencies are installed automatically
./capcat list sources

# Or use the Python wrapper directly
python3 run_capcat.py list sources
```

**What happens automatically**:
1. Detects or creates virtual environment
2. Installs all dependencies from requirements.txt
3. Activates proper Python environment
4. Executes capcat with dependencies available

### Manual Installation

If you prefer manual control over the environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import requests, bs4, yaml, markdownify, markdown, pygments; print('All dependencies installed')"
```

### System-Wide Installation (Not Recommended)

```bash
# Install globally (may conflict with other projects)
pip3 install -r requirements.txt
```

## Dependency Management

### Virtual Environment Benefits

- **Isolation**: Prevents conflicts with other Python projects
- **Consistency**: Ensures all team members use same package versions
- **Reproducibility**: Identical environments across different systems
- **Easy Cleanup**: Can delete entire venv directory to start fresh

### Requirements File Structure

```text
requests              # HTTP library for web requests
beautifulsoup4        # HTML parsing and extraction
PyYAML               # YAML configuration file support
markdownify          # HTML to Markdown conversion
markdown>=3.5.0      # Markdown processing with version constraint
pygments>=2.16.0     # Syntax highlighting with version constraint
```

### Version Pinning Strategy

- **Core libraries**: Latest versions for security and features
- **Critical dependencies**: Minimum version constraints for compatibility
- **Development**: Consider pinning exact versions for reproducibility

## Wrapper System Architecture

### Python Wrapper (`run_capcat.py`)

The Python wrapper handles all dependency-related tasks:

```python
class CapcatWrapper:
    def get_python_executable(self):
        """Detects and configures Python environment."""

    def create_virtual_environment(self):
        """Creates venv if none exists."""

    def install_dependencies(self, python_exe):
        """Installs packages from requirements.txt."""
```

### Bash Shortcut (`capcat`)

Minimal script that delegates to Python wrapper:

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
exec python3 "${SCRIPT_DIR}/run_capcat.py" "$@"
```

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'markdown'"

**Cause**: Dependencies not installed or virtual environment not activated

**Solution**:
```bash
# Let wrapper handle it automatically
./capcat list sources

# Or install manually
source venv/bin/activate && pip install -r requirements.txt
```

#### "Python 3 is required but not installed"

**Cause**: Python 3 not available in system PATH

**Solution**:
- macOS: `brew install python@3.11`
- Ubuntu: `sudo apt install python3 python3-pip python3-venv`
- Windows: Download from python.org

#### Virtual Environment Creation Fails

**Cause**: Insufficient permissions or corrupted Python installation

**Solution**:
```bash
# Clean and recreate
rm -rf venv
python3 -m venv venv --clear
```

#### Package Installation Timeout

**Cause**: Network issues or slow package index

**Solution**:
```bash
# Use different index
pip install -r requirements.txt --index-url https://pypi.org/simple/

# Increase timeout
pip install -r requirements.txt --timeout 120
```

### Dependency Conflicts

#### Version Conflicts

**Symptoms**: ImportError, AttributeError, or unexpected behavior

**Solution**:
```bash
# Check installed versions
pip list

# Update conflicting packages
pip install --upgrade package_name

# Recreate environment if necessary
rm -rf venv && ./capcat list sources
```

#### System vs Virtual Environment

**Issue**: System packages interfering with virtual environment

**Solution**:
```bash
# Ensure clean virtual environment
python3 -m venv venv --clear
source venv/bin/activate
pip install -r requirements.txt
```

## Development Dependencies

For development and testing, additional packages may be required:

```bash
# Development requirements (not in main requirements.txt)
pip install pytest pytest-cov flake8 black mypy
```

### Testing Dependencies

```bash
# Run dependency tests
python3 -c "
import sys
required = ['requests', 'bs4', 'yaml', 'markdownify', 'markdown', 'pygments']
missing = []
for module in required:
    try:
        __import__(module)
        print(f'[OK] {module}')
    except ImportError:
        missing.append(module)
        print(f'✗ {module}')

if missing:
    print(f'Missing: {missing}')
    sys.exit(1)
else:
    print('All dependencies available')
"
```

## Performance Considerations

### Connection Pooling

`requests` library is configured with connection pooling:

```python
# In core/config.py
pool_connections: int = 20
pool_maxsize: int = 20
```

### Memory Usage

Typical memory usage by dependency:
- `requests`: ~10MB baseline
- `beautifulsoup4`: ~5MB per parsed document
- `markdown`: ~3MB for processing
- `pygments`: ~8MB for syntax highlighting

## Security Considerations

### Package Sources

- All packages installed from PyPI (pypi.org)
- No custom or private package indexes
- Regular security updates recommended

### Virtual Environment Security

```bash
# Verify package integrity
pip check

# List installed packages and versions
pip freeze

# Audit for security vulnerabilities (requires pip-audit)
pip install pip-audit && pip-audit
```

## Version History

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Date</th>
      <th>Change</th>
      <th>Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-21</td>
      <td>Added wrapper system</td>
      <td>Automatic dependency management</td>
    </tr>
    <tr>
      <td>2025-01-21</td>
      <td>Updated markdown version</td>
      <td>Improved HTML generation</td>
    </tr>
    <tr>
      <td>2025-01-21</td>
      <td>Added pygments constraint</td>
      <td>Consistent syntax highlighting</td>
    </tr>
  </tbody>
</table>
</div>

## Related Documentation

- [Installation Guide](quick-start.html)
- [Configuration](tutorials/03-configuration-exhaustive.html)
- [Troubleshooting](troubleshooting.html)

---

**Note**: This documentation is automatically maintained. For the most current dependency information, always refer to `requirements.txt` in the project root.