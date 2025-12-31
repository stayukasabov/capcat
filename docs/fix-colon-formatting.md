# Fix Colon Formatting

Technical documentation for `fix_colon_formatting.py` - removes leading colons from HTML lines.

## Problem Statement

HTML files in `website/docs/` contain incorrectly formatted lines where content starts with `:` on a new line after headers:

```html
<h4>Base Templates</h4>
: htmlgen/base/templates/ using clean {{}} syntax
```

This creates rendering issues and should be:

```html
<h4>Base Templates</h4>
htmlgen/base/templates/ using clean {{}} syntax
```

## Solution

Pattern-based line processor that:
1. Identifies lines starting with `:` (with optional leading whitespace)
2. Removes the `:` and immediately following space
3. Preserves all indentation
4. Ignores colons in URLs, code, attributes, or middle of lines

## Pattern Matching

**Regex:** `^\s*:\s*(.*)$`

**Components:**
- `^` - Start of line
- `\s*` - Zero or more whitespace (captured for preservation)
- `:` - The literal colon to remove
- `\s*` - Optional space(s) after colon (removed)
- `(.*)` - Rest of line content (preserved)
- `$` - End of line

**Match Examples:**
```
": content"              → "content"
"  : content"            → "  content"
"\t: content"            → "\tcontent"
":    multiple spaces"   → "   multiple spaces"
```

**Non-Match Examples:**
```
"text: value"            → No match (colon not at start)
"https://example.com"    → No match
"def func(): pass"       → No match
```

## Architecture

### ColonFormattingFixer Class

**Attributes:**
- `PATTERN`: Compiled regex pattern
- `dry_run`: Preview mode flag
- `create_backup`: Backup creation flag
- `stats`: Dictionary tracking modifications

**Methods:**

#### `fix_line(line: str) -> Tuple[str, bool]`
Processes single line.

**Returns:** `(fixed_line, was_modified)`

**Logic:**
1. Match pattern against line
2. If match: extract indentation + content
3. Reconstruct: `indent + content`
4. Preserve line ending (if present)
5. Return modified line + True
6. If no match: return original + False

**Complexity:** O(1) per line

#### `fix_file(filepath: Path) -> int`
Processes entire file.

**Algorithm:**
1. Read all lines
2. Process each line through `fix_line()`
3. Collect modified lines
4. If changes detected:
   - Dry run: print preview
   - Live mode: create backup, write changes
5. Return change count

**Complexity:** O(n) where n = line count

#### `process_directory(directory: Path) -> None`
Recursive directory processor.

**Algorithm:**
1. Find all `*.html` files recursively
2. Process each file via `fix_file()`
3. Accumulate statistics
4. Print summary

**Complexity:** O(f × n) where f = file count, n = avg lines

### Statistics Tracking

**Metrics:**
- `files_scanned`: Total HTML files processed
- `files_modified`: Files with changes
- `lines_changed`: Total lines modified
- `backups_created`: Backup files created

## Usage

### Basic Commands

```bash
# Preview changes
python3 fix_colon_formatting.py --dry-run

# Apply with backups (default)
python3 fix_colon_formatting.py

# Apply without backups
python3 fix_colon_formatting.py --no-backup

# Custom directory
python3 fix_colon_formatting.py --dir ../other/path
```

### Workflow

**1. Preview First:**
```bash
python3 fix_colon_formatting.py --dry-run
```

**2. Review Output:**
```
Found 15 HTML files to scan

[DRY RUN] Would modify website/docs/architecture.html
  Lines to change: 3
  Line 45:
    Before: : htmlgen/base/templates/ using clean {{}} syntax
    After:  htmlgen/base/templates/ using clean {{}} syntax
```

**3. Apply Changes:**
```bash
python3 fix_colon_formatting.py
```

**4. Verify Results:**
```bash
# Check modified file
cat website/docs/architecture.html

# Check backup exists
ls -la website/docs/*.bak
```

**5. Restore if Needed:**
```bash
mv website/docs/architecture.html.bak website/docs/architecture.html
```

## Test Suite

**File:** `test_colon_formatting.py`

**Coverage:**
- Basic colon removal
- Indentation preservation (spaces/tabs/mixed)
- Non-matching patterns (URLs, code, attributes)
- Edge cases (empty lines, unicode, long lines)
- Real-world examples

**Run Tests:**
```bash
# Manual tests only
python3 test_colon_formatting.py

# With pytest (if available)
pytest test_colon_formatting.py -v
```

**Test Categories:**

**1. Basic Transformation:**
- Line starting with colon
- Line with whitespace then colon
- Tab-indented colon lines

**2. Indentation Preservation:**
- Space indentation
- Tab indentation
- Mixed whitespace
- Multiple levels

**3. Non-Modifications:**
- Colon in middle of line
- URLs with colons
- Code syntax (Python type hints)
- HTML attributes
- CSS styles
- Time formats (10:30:45)
- Ratios (16:9)

**4. Edge Cases:**
- Empty colon lines
- Colon-only lines
- Unicode content
- Very long lines
- Windows line endings
- No line ending (EOF)

## Pattern Analysis

### What Gets Modified

**Pattern:** Line starts with optional whitespace + colon

```html
: htmlgen/base/templates/               → Modified
  : htmlgen/[source]/templates/         → Modified
    : Indented content                  → Modified
:                                       → Modified (empty)
```

### What Stays Unchanged

**Pattern:** Colon not at start

```html
<h4>Title</h4>                          → Unchanged
Normal text: with colon                 → Unchanged
https://example.com:8080                → Unchanged
def function(arg: str) -> None:         → Unchanged
"key": "value"                          → Unchanged
Time: 10:30:45                          → Unchanged
```

## Safety Features

### Backup System

**Default:** Enabled (use `--no-backup` to disable)

**Mechanism:**
- Original: `file.html`
- Backup: `file.html.bak`
- Overwrite protection: Yes (existing `.bak` overwritten)

**Restore:**
```bash
mv file.html.bak file.html
```

### Dry-Run Mode

**Default:** Off (use `--dry-run` to enable)

**Features:**
- No file modifications
- No backups created
- Shows preview of changes
- Displays first 3 changes per file
- Full statistics reported

### Atomic Operations

**File Processing:**
1. Read entire file into memory
2. Process all lines
3. If changes: write entire file at once
4. No partial modifications on error

**Error Handling:**
- File read errors: skip file, continue processing
- Unicode decode errors: skip file, report error
- Write errors: original file unchanged (backup preserves state)

## Performance

**Optimization Strategies:**

1. **Compiled Regex:** Pattern compiled once, reused for all lines
2. **Single Pass:** Each line processed exactly once
3. **In-Memory:** Small HTML files fully loaded (fast I/O)
4. **Lazy Recursion:** `rglob()` returns iterator, not list

**Complexity:**
- Per line: O(1)
- Per file: O(n) where n = lines
- Per directory: O(f × n) where f = files

**Benchmarks:**
- Small file (100 lines): <1ms
- Medium file (1000 lines): <10ms
- Large directory (100 files): <1s

## Integration

### With Version Control

**Git Workflow:**
```bash
# Create branch
git checkout -b fix/colon-formatting

# Preview changes
python3 fix_colon_formatting.py --dry-run

# Apply fixes
python3 fix_colon_formatting.py

# Review diff
git diff website/docs/

# Commit
git add website/docs/
git commit -m "Fix leading colon formatting in HTML docs"

# Push
git push origin fix/colon-formatting
```

### With CI/CD

**Pre-commit Hook:**
```bash
#!/bin/bash
python3 fix_colon_formatting.py --dry-run
if [ $? -ne 0 ]; then
    echo "Colon formatting issues found"
    exit 1
fi
```

**Validation Script:**
```bash
# Check for remaining colon patterns
grep -r "^[[:space:]]*:" website/docs/*.html
```

## Troubleshooting

### No Files Found

**Problem:** "No HTML files found in website/docs"

**Solutions:**
1. Check directory exists: `ls -la website/docs`
2. Check for HTML files: `find website/docs -name "*.html"`
3. Use absolute path: `--dir /full/path/to/docs`

### No Changes Detected

**Problem:** Script runs but reports 0 changes

**Causes:**
1. Files already fixed
2. Pattern doesn't match (colon not at line start)
3. Wrong directory specified

**Verify:**
```bash
# Look for pattern
grep "^[[:space:]]*:" website/docs/*.html

# Check sample file
head -20 website/docs/sample.html
```

### Unicode Errors

**Problem:** "Error reading file: codec error"

**Solution:**
- File may have mixed encoding
- Script assumes UTF-8
- Convert file: `iconv -f ISO-8859-1 -t UTF-8 file.html`

### Permission Errors

**Problem:** "Permission denied"

**Solution:**
```bash
# Make script executable
chmod +x fix_colon_formatting.py

# Check file permissions
ls -la website/docs/*.html

# Fix permissions
chmod 644 website/docs/*.html
```

## Limitations

### Known Edge Cases

**1. Markdown in HTML Comments:**
```html
<!--
: This is markdown-style list
-->
```
Will be modified (colon removed). Workaround: use different list syntax.

**2. Literal Colon Display:**
```html
<pre>: This should display with colon</pre>
```
Will be modified if colon at line start. Workaround: add space before colon.

**3. YAML/JSON Embedded:**
```html
<script type="application/ld+json">
{
  "key": "value"
}
</script>
```
Safe - colon not at line start.

### Scope

**Targets:** Lines starting with colon

**Ignores:**
- Colons in URLs, code, attributes
- Colons in middle of lines
- Comment contents (unless colon at line start)
- Script/style tag contents (unless colon at line start)

## Examples

### Before/After

**Input:**
```html
<h4>Base Templates</h4>
: htmlgen/base/templates/ using clean {{}} syntax

<h4>Source Overrides</h4>
  : htmlgen/[source]/templates/ for custom layouts

<h4>Code Example</h4>
def function(arg: str) -> None:
    return None
```

**Output:**
```html
<h4>Base Templates</h4>
htmlgen/base/templates/ using clean {{}} syntax

<h4>Source Overrides</h4>
  htmlgen/[source]/templates/ for custom layouts

<h4>Code Example</h4>
def function(arg: str) -> None:
    return None
```

**Changes:** 2 lines modified (lines 2, 5)

### Batch Processing

**Scenario:** Fix 50 HTML files

```bash
# Preview all
python3 fix_colon_formatting.py --dry-run

# Output:
# Found 50 HTML files to scan
# Files modified: 12
# Lines changed: 34

# Apply
python3 fix_colon_formatting.py

# Verify
ls -la website/docs/*.bak  # 12 backups created
```

## Implementation Details

### Line Ending Preservation

**Logic:**
```python
if line.endswith('\n'):
    return f"{indent}{content}\n", True
else:
    return f"{indent}{content}", True
```

**Handles:**
- Unix: `\n`
- Windows: `\r\n` (preserved in content)
- Mac Classic: `\r` (preserved in content)
- No ending: EOF line

### Indentation Preservation

**Capture:** `(\s*)` in pattern

**Includes:**
- Spaces: ` `
- Tabs: `\t`
- Mixed: `\t  \t`
- Unicode spaces: preserved

**Reconstruction:**
```python
indent = match.group(1)  # Captured whitespace
content = match.group(2)  # Rest of line
return f"{indent}{content}\n"
```

### Statistics Aggregation

**Per-File:**
```python
changes_count = 0
for line in lines:
    fixed, modified = fix_line(line)
    if modified:
        changes_count += 1
```

**Global:**
```python
self.stats['files_modified'] += 1
self.stats['lines_changed'] += changes_count
```

## Related Scripts

**Similar Pattern:**
- `fix_author_links.py` - Link text replacement
- `fix_nbsp_after_headers.py` - Remove `&nbsp;` after headers
- `fix_colon_formatting.py` - Remove leading colons (this script)

**Common Framework:**
- Line-by-line processing
- Regex pattern matching
- Dry-run mode
- Backup system
- Statistics tracking

## References

**Regex Documentation:**
- Python `re` module: https://docs.python.org/3/library/re.html
- Regex patterns: https://regex101.com/

**Related Files:**
- Implementation: `fix_colon_formatting.py`
- Tests: `test_colon_formatting.py`
- Samples: `website/docs/test/sample.html`
