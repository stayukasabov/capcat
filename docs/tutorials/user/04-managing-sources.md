# Managing Your Sources

Add, remove, test, and organize news sources in Capcat.

## What You'll Learn

- Add new RSS sources quickly
- Remove unused sources safely
- Test source health
- Organize sources effectively

## Quick Source Management

### List Current Sources

See what's available:

```bash
./capcat list sources
```

Output organized by category:
```
TECH:
  - hn             Hacker News
  - lb             Lobsters
  - iq             InfoQ

NEWS:
  - bbc            BBC News
  - guardian       The Guardian

SCIENCE:
  - nature         Nature News

Total: 15 sources
```

## Adding New Sources

### Method 1: Quick Add (RSS)

Add an RSS source in one command:

```bash
./capcat add-source --url https://techcrunch.com/feed/
```

Interactive prompts:
```
[OK] Feed 'TechCrunch' found.
Source ID: techcrunch
Category: tech
Add to bundle? Yes
  Bundle: tech
Test fetch? Yes
[OK] Source added successfully!
```

### Method 2: Interactive Add

Use the visual menu:

```bash
./capcat catch
# Select: Manage Sources
# Select: Add New Source from RSS Feed
# Paste URL
```

### Method 3: Custom Source Config

For complex sources:

```bash
./capcat generate-config
```

Interactive wizard for:
- Source ID and name
- Category
- Discovery method (RSS or HTML)
- Content selectors
- Image processing
- Rate limiting

## Removing Sources

### Safe Removal with Backup

Remove sources interactively:

```bash
./capcat remove-source
```

Process:
```
Select sources to remove:
  [ ] hn              Hacker News
  [x] oldsite         Old Site
  [x] discontinued    Discontinued

Confirm removal? Yes
[OK] Backup created: .capcat-backups/backup_20251126_100000/
[OK] 2 sources removed
```

### Preview Before Removing

See what would be removed:

```bash
./capcat remove-source --dry-run
```

Shows:
- Files that would be deleted
- Bundle entries that would be removed
- No actual changes made

### Undo Removal

Restore last removed sources:

```bash
./capcat remove-source --undo
```

Or restore specific backup:

```bash
./capcat remove-source --undo backup_20251126_100000
```

## Testing Sources

### Test Single Source

Verify a source works:

```bash
./capcat fetch sourcename --count 3
```

Success indicators:
- Fetches 3 articles
- No errors
- Articles saved correctly

### Test in Interactive Mode

```bash
./capcat catch
# Select: Manage Sources
# Select: Test a Source
# Choose source
# View results
```

### Troubleshoot Failed Sources

If a source fails:

1. Check the error message
2. Verify RSS feed still exists
3. Test with low count first: `--count 1`
4. Check source configuration

Common fixes:
```bash
# RSS feed might have changed
# Edit config
vim sources/active/config_driven/configs/sourcename.yaml

# Update feed_url if RSS moved
# Save and test again
./capcat fetch sourcename --count 3
```

## Source Organization

### Group by Category

Sources auto-group by category field in config.

View by category:
```bash
./capcat list sources
```

### Add to Bundles

Include source in bundle:

```bash
vim sources/active/bundles.yml
```

Add to existing bundle:
```yaml
tech:
  sources:
    - hn
    - lb
    - newsource  # Add here
```

Or let bundle auto-discover by matching category:
- Bundle named "tech" auto-includes sources with category: "tech"
- No manual editing needed

### Create Source Categories

When adding source, assign meaningful category:
- tech - Technology news
- news - General news
- science - Scientific articles
- ai - AI/ML content
- sports - Sports news

## Finding RSS Feeds

### Common RSS Feed Patterns

Try these URL patterns:

```
https://example.com/feed
https://example.com/rss
https://example.com/feed.xml
https://example.com/rss.xml
https://example.com/feed/
```

### Verify RSS Feed

Test in browser first:
```
https://techcrunch.com/feed/
```

Should show XML with articles.

## Source Configuration Files

### Config-Driven Sources

Location: `sources/active/config_driven/configs/`

Simple YAML:
```yaml
display_name: "Example News"
base_url: "https://example.com/"
category: "tech"
timeout: 10.0
rate_limit: 1.0

article_selectors:
  - ".headline a"

content_selectors:
  - ".article-content"
```

### Custom Sources

Location: `sources/active/custom/sourcename/`

Contains:
- `source.py` - Python implementation
- `config.yaml` - Configuration

Use for complex sources with:
- Comment systems
- Special authentication
- Complex parsing logic

## Maintenance Tasks

### Monthly Source Check

Test all sources:

```bash
# List sources
./capcat list sources

# Test each that matters to you
./capcat fetch hn --count 3
./capcat fetch bbc --count 3
./capcat fetch nature --count 3
```

### Clean Up Unused Sources

Remove sources you don't use:

```bash
./capcat remove-source
# Select unused sources
# Confirm removal
```

### Update Source Configs

If source changes their website:

```bash
# Edit config
vim sources/active/config_driven/configs/sourcename.yaml

# Update selectors or URLs
# Test
./capcat fetch sourcename --count 3
```

## Pro Tips

**Quick Testing:**
- Always use `--count 3` for tests
- Check both article content and images
- Verify date is recent

**Safe Removal:**
- Use `--dry-run` first
- Backups are automatic
- Can undo anytime

**Organization:**
- Use clear source IDs (lowercase, no spaces)
- Assign accurate categories
- Add to appropriate bundles

**Discovery:**
- Many sites have RSS feeds
- Look for RSS icon in browser
- Try common feed URL patterns

## Common Issues

**Source not found:**
```bash
# Refresh registry
./capcat list sources

# Verify file exists
ls sources/active/config_driven/configs/sourcename.yaml
```

**Feed URL changed:**
```bash
# Update config
vim sources/active/config_driven/configs/sourcename.yaml
# Change rss_url
# Test
./capcat fetch sourcename --count 3
```

**Source has anti-bot protection:**
- Use RSS feed instead of HTML scraping
- RSS bypasses most anti-bot systems
- Add source via RSS URL

## Next Steps

**Organize better:**
- [Bundles](05-bundles.html) - Group sources efficiently
- [Customizing Output](06-customizing-output.html) - Control what you collect

**Technical details:**
- [Source System Exhaustive](../04-source-system-exhaustive.html) - Complete source system reference
- [Configuration Exhaustive](../03-configuration-exhaustive.html) - All configuration options

## Quick Reference

```bash
# Add source
./capcat add-source --url RSS_URL

# Remove source
./capcat remove-source

# Test source
./capcat fetch SOURCE --count 3

# List sources
./capcat list sources

# Generate config
./capcat generate-config

# Undo removal
./capcat remove-source --undo
```
