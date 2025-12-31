# Help System Enhancement Design

**Date:** 2025-12-23
**Goal:** Add real, practical examples to all CLI command help pages
**Method:** TDD approach with example verification

## Current State

**Problem:** Help pages show only usage syntax and option descriptions
- No examples
- Users must guess correct syntax
- No demonstration of real use cases

**Exception:** `remove-source` already has examples (good model to follow)

## Design Principles

1. **Real Examples:** Use actual source names (hn, bbc, nature)
2. **Progressive Complexity:** Simple → Intermediate → Advanced
3. **Common Use Cases:** Show what users actually need
4. **Consistent Format:** Match existing `remove-source` style
5. **Verified:** All examples must work

## Enhanced Help Format

### Template Structure

```
usage: capcat <command> [options] <args>

positional arguments:
  ...

options:
  ...

Examples:
  <Simple example with description>
  <Intermediate example>
  <Advanced example>
  <Edge case or special usage>
```

## Command-by-Command Design

### 1. single Command

**Current Help:** Basic usage only

**Enhanced Help:**
```
Examples:
  # Download single article
  capcat single https://news.ycombinator.com/item?id=12345

  # Download with HTML generation
  capcat single https://bbc.com/news/technology-12345 --html

  # Download all media (images, videos, documents)
  capcat single https://nature.com/articles/12345 --media

  # Save to custom directory
  capcat single URL --output ~/Articles

  # Download with verbose logging to file
  capcat single URL --verbose --log-file download.log

  # Update previously downloaded article
  capcat single URL --update
```

### 2. fetch Command

**Current Help:** Basic usage only

**Enhanced Help:**
```
Examples:
  # Fetch from single source (use './capcat list sources' to see all)
  capcat fetch hn

  # Fetch specific number of articles
  capcat fetch hn --count 10

  # Fetch from multiple sources
  capcat fetch hn,bbc,nature --count 15

  # Fetch with HTML generation
  capcat fetch hn,lb --html

  # Fetch all media types
  capcat fetch bbc --media --count 5

  # Save to custom directory
  capcat fetch hn --output ~/News --count 20

  # Fetch with verbose output and logging
  capcat fetch hn,bbc --verbose --log-file fetch.log
```

### 3. bundle Command

**Current Help:** Shows available bundles in choices, but no examples

**Enhanced Help:**
```
Examples:
  # Fetch tech news bundle (use './capcat list bundles' to see all)
  capcat bundle tech

  # Fetch specific number from bundle
  capcat bundle tech --count 10

  # Fetch news bundle with HTML
  capcat bundle news --html

  # Fetch science articles with all media
  capcat bundle science --media --count 5

  # Fetch all available bundles
  capcat bundle --all

  # Save to custom directory
  capcat bundle tech --output ~/TechNews

  # Verbose mode with logging
  capcat bundle tech --verbose --log-file bundle.log --count 15
```

### 4. list Command

**Current Help:** Minimal

**Enhanced Help:**
```
Examples:
  # List all available sources grouped by category
  capcat list sources

  # List available bundles
  capcat list bundles

  # List both sources and bundles
  capcat list
  capcat list all
```

### 5. add-source Command

**Current Help:** Basic

**Enhanced Help:**
```
Examples:
  # Add new source from RSS feed (interactive prompts follow)
  capcat add-source --url https://example.com/feed.xml

  # The command will prompt you for:
  #   - Source ID (slug name)
  #   - Category (tech, news, science, etc.)
  #   - Bundle assignment (optional)
  #   - Test fetch (recommended)
```

### 6. generate-config Command

**Current Help:** Basic

**Enhanced Help:**
```
Examples:
  # Start interactive configuration generator
  capcat generate-config

  # Follow prompts to create comprehensive YAML configuration
  # Output: sources/active/config_driven/configs/yoursource.yaml
```

### 7. catch Command

**Current Help:** Basic

**Enhanced Help:**
```
Examples:
  # Start interactive mode (menu-driven interface)
  capcat catch

  # Interactive mode features:
  #   - No command memorization needed
  #   - Visual source/bundle selection
  #   - Guided workflows
  #   - Source management
```

### 8. Main Help (Global)

**Enhanced Main Help:**
```
Examples:
  # Quick start - fetch tech news
  capcat bundle tech --count 10

  # Download single article
  capcat single https://news.ycombinator.com/item?id=12345

  # See available sources
  capcat list sources

  # Interactive mode (easiest for beginners)
  capcat catch

  # Get help on any command
  capcat <command> --help
```

## Implementation Strategy

### Phase 1: TDD Tests (RED)

Create `tests/test_help_examples.py`:
- Verify each example command is syntactically valid
- Test that examples use real source names
- Verify examples appear in help output
- Check formatting consistency

### Phase 2: Implementation (GREEN)

Update `cli.py` `create_parser()` function:
- Add epilog to each subparser
- Use RawDescriptionHelpFormatter (already set)
- Format examples with proper indentation
- Ensure consistent style

### Phase 3: Verification

- Manual testing: Run each example command
- Automated testing: Verify help output contains examples
- Documentation: Update any docs referencing help

## Example Source Names (Real)

**Use these in examples:**
- **Tech:** hn, lb, iq, ieee, mashable
- **News:** bbc, guardian
- **Science:** nature, scientificamerican
- **AI:** mitnews, google-reserch
- **Sports:** bbcsport

**Bundles:**
- tech, techpro, news, science, ai, sports, all

## Formatting Rules

1. **Indentation:** 2 spaces for examples
2. **Comments:** # for inline explanations
3. **Line Length:** Max 78 characters
4. **Grouping:** Blank line between example groups
5. **Consistency:** Match `remove-source` format exactly

## Testing Requirements

### Automated Tests

```python
def test_single_help_has_examples():
    """Verify single command help includes examples."""
    result = subprocess.run(['./capcat', 'single', '--help'],
                           capture_output=True, text=True)
    assert 'Examples:' in result.stdout
    assert 'https://news.ycombinator.com' in result.stdout

def test_examples_use_real_sources():
    """Verify examples use actual source names."""
    sources = get_available_sources()
    result = subprocess.run(['./capcat', 'fetch', '--help'],
                           capture_output=True, text=True)
    # Should contain at least one real source name
    assert any(source in result.stdout for source in sources.keys())
```

### Manual Verification

Run each example to ensure it works:
```bash
# Test single examples
./capcat single https://news.ycombinator.com/item?id=12345 --dry-run

# Test fetch examples
./capcat fetch hn --count 1 --dry-run

# Test bundle examples
./capcat bundle tech --count 1 --dry-run
```

## Success Criteria

✅ Every command has 3-6 real examples
✅ Examples use actual source/bundle names
✅ Help output is readable and well-formatted
✅ All examples are verified to work
✅ Tests prevent regression
✅ Consistent style across all commands

## Implementation Checklist

- [ ] Write TDD tests for help examples
- [ ] Update `single` command help
- [ ] Update `fetch` command help
- [ ] Update `bundle` command help
- [ ] Update `list` command help
- [ ] Update `add-source` command help
- [ ] Update `generate-config` command help
- [ ] Update `catch` command help
- [ ] Update main `--help` epilog
- [ ] Run all tests
- [ ] Manual verification of each example
- [ ] Document changes

## Estimated Effort

- Design: ✅ Complete
- Tests: 30 minutes
- Implementation: 45 minutes
- Verification: 30 minutes
- **Total:** ~1.75 hours

---

**Next Step:** Write TDD tests for help examples
