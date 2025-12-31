# Dependency Management System

Comprehensive automated dependency management for Capcat with intelligent error detection and repair mechanisms.

## Overview

The refactored dependency management system provides:
- Automatic virtual environment validation and repair
- Intelligent corruption detection (hardcoded paths, missing files, broken executables)
- Multi-level fallback mechanisms
- Comprehensive logging and diagnostics
- Simple CLI interface for common operations

## Components

### 1. Enhanced Dependency Setup Script
**Location:** `scripts/setup_dependencies.py`

Comprehensive Python-based dependency manager with:
- Virtual environment validation and corruption detection
- Automatic repair mechanisms
- Dependency verification (actual import testing)
- Dependency caching for performance
- Detailed verbose logging

**Usage:**
```bash
# Normal setup (auto-detects and fixes issues)
python3 scripts/setup_dependencies.py

# Force complete rebuild
python3 scripts/setup_dependencies.py --force-rebuild

# Validation only (no changes)
python3 scripts/setup_dependencies.py --check-only

# Verbose logging
python3 scripts/setup_dependencies.py --verbose
```

### 2. Quick Fix Script
**Location:** `scripts/fix_dependencies.sh`

User-friendly bash wrapper with simple interface:

```bash
# Quick fix (most common case)
./scripts/fix_dependencies.sh

# Force complete rebuild
./scripts/fix_dependencies.sh --force

# Check dependencies only
./scripts/fix_dependencies.sh --check
```

### 3. Enhanced Wrapper
**Location:** `run_capcat.py` (refactored)

Integrated into the main Capcat wrapper with:
- Automatic dependency validation before each run
- Intelligent repair attempts on validation failure
- Custom exception hierarchy for better error handling
- Fallback to system Python when venv unavailable

## Common Issues and Solutions

### Issue: Hardcoded Path Corruption

**Symptoms:**
```
venv/bin/pip: line 2: /Users/xpro/...: No such file or directory
```

**Cause:**
Virtual environment contains absolute paths from previous location.

**Solution:**
```bash
./scripts/fix_dependencies.sh --force
```

### Issue: Missing Dependencies

**Symptoms:**
```
Missing dependencies: ['requests', 'beautifulsoup4', ...]
```

**Solution:**
```bash
./scripts/fix_dependencies.sh
```

### Issue: Broken Virtual Environment

**Symptoms:**
- Python executable doesn't work
- Missing essential venv files
- Import errors for installed packages

**Solution:**
```bash
python3 scripts/setup_dependencies.py --force-rebuild
```

## Manual Dependency Setup

If automated tools fail, manual setup:

```bash
# 1. Remove broken venv
rm -rf venv

# 2. Create fresh venv
python3 -m venv venv

# 3. Activate venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python3 scripts/setup_dependencies.py --check-only
```

## Integration with Capcat Wrapper

The enhanced wrapper (`run_capcat.py`) automatically:

1. **Pre-execution validation**: Checks dependencies before running capcat.py
2. **Automatic repair**: Attempts to fix issues when detected
3. **Fallback mechanisms**: Uses system Python if venv unavailable
4. **Clear error messages**: Provides actionable instructions on failure

No user intervention required for normal operation.

## Exit Codes

The dependency system uses specific exit codes:

- `0`: Success
- `1`: General error
- `2`: Dependency error (automatic repair failed)
- `3`: Execution error
- `130`: User interrupted (Ctrl+C)

## Validation Process

The system validates dependencies by:

1. **File structure check**: Verifies essential venv files exist
2. **Executable test**: Runs `python --version` from venv
3. **Import testing**: Attempts to import each required package
4. **Path verification**: Checks pyvenv.cfg for valid Python home path

## Performance Optimizations

- **Dependency caching**: Avoids redundant package checks
- **Lazy validation**: Only validates when needed
- **Parallel operations**: Future enhancement for faster setup

## Troubleshooting

### Verbose Mode

Enable detailed logging for diagnostics:

```bash
python3 scripts/setup_dependencies.py --verbose --force-rebuild
```

### Check-Only Mode

Validate without making changes:

```bash
./scripts/fix_dependencies.sh --check
```

### Manual Inspection

Check virtual environment health:

```bash
# Check venv structure
ls -la venv/bin/

# Test venv Python
venv/bin/python --version

# Check installed packages
venv/bin/pip list

# Inspect pyvenv.cfg
cat venv/pyvenv.cfg
```

## Best Practices

1. **Use the wrapper**: Always run `./capcat` instead of directly running `python capcat.py`
2. **Regular validation**: Periodically run `--check-only` to detect issues early
3. **Clean rebuilds**: Use `--force` when moving project to new location
4. **Keep dependencies minimal**: Only add truly required packages to requirements.txt

## Advanced Usage

### Custom Requirements File

```bash
python3 scripts/setup_dependencies.py --requirements custom-requirements.txt
```

### Dependency Cache Location

Cache stored at: `venv/.dependency_cache.json`

Contains:
- Timestamp of last validation
- Installed package versions
- Python executable path

### Integration with CI/CD

```bash
# CI pipeline example
python3 scripts/setup_dependencies.py --check-only || \
  python3 scripts/setup_dependencies.py --force-rebuild
```

## Future Enhancements

Planned improvements:
- Offline dependency installation from cache
- Parallel package installation
- Automatic requirements.txt updates
- Version conflict detection
- Dependency graph visualization
- Integration with package managers (brew, apt)

## Support

If automated dependency management fails:

1. Check this documentation for common issues
2. Run with `--verbose` flag for detailed diagnostics
3. Try manual setup steps
4. Report persistent issues with full error output