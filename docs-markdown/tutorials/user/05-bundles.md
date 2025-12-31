# Organizing with Bundles

Group sources for efficient one-command collection.

## What You'll Learn

- Use pre-made bundles
- Create custom bundles
- Manage bundle sources
- Optimize your workflow

## What Are Bundles?

Bundles are named groups of sources you can fetch from with one command.

Instead of:
```bash
./capcat fetch hn --count 20
./capcat fetch lb --count 20
./capcat fetch iq --count 20
```

Use:
```bash
./capcat bundle techpro --count 20
```

## Pre-Made Bundles

### tech - Consumer Technology
```bash
./capcat bundle tech --count 20
```

Sources:
- IEEE Spectrum
- Mashable
- Gizmodo

**Use for:** General tech news, consumer electronics, gadgets

### techpro - Professional Developer
```bash
./capcat bundle techpro --count 15
```

Sources:
- Hacker News (with comments)
- Lobsters
- InfoQ

**Use for:** Programming, software development, technical discussions

### news - General News
```bash
./capcat bundle news --count 25
```

Sources:
- BBC News
- The Guardian

**Use for:** World news, current events

### science - Scientific Research
```bash
./capcat bundle science --count 20
```

Sources:
- Nature News
- Scientific American

**Use for:** Scientific discoveries, research papers

### ai - AI & Machine Learning
```bash
./capcat bundle ai --count 20
```

Sources:
- MIT News

**Use for:** AI developments, ML research

### sports - Sports News
```bash
./capcat bundle bbcsport --count 25
```

Sources:
- BBC Sport

**Use for:** Sports coverage, match reports

### all - Everything
```bash
./capcat bundle all --count 10
```

**Use for:** Sample from all available sources

## List Available Bundles

See all bundles:

```bash
./capcat list bundles
```

Output:
```
--- Available Bundles ---

tech - Consumer Technology
  Sources: ieee, mashable, gizmodo

techpro - Professional Developer
  Sources: hn, lb, iq

news - General News
  Sources: bbc, guardian

Total: 6 bundles
```

## Creating Custom Bundles

### Method 1: Edit Configuration File

```bash
vim sources/active/bundles.yml
```

Add your bundle:

```yaml
mybundle:
  description: "My custom news bundle"
  sources:
    - hn
    - bbc
    - nature
    - mitnews
  default_count: 15
```

Save and use:

```bash
./capcat bundle mybundle
```

### Method 2: Interactive Bundle Management

```bash
./capcat catch
# Select: Manage Sources
# Select: Manage Bundles
# Select: Create New Bundle
```

Follow prompts to:
- Name your bundle
- Add sources
- Set default count
- Save

## Bundle Examples

### Morning Briefing Bundle

Quick overview of everything:

```yaml
morning:
  description: "Morning news briefing"
  sources:
    - bbc
    - hn
    - nature
  default_count: 10
```

Use:
```bash
./capcat bundle morning --html
```

### Research Bundle

Deep dive articles with media:

```yaml
research:
  description: "Research and academic content"
  sources:
    - nature
    - scientificamerican
    - mitnews
  default_count: 30
```

Use:
```bash
./capcat bundle research --media --html
```

### Weekend Reading Bundle

Long-form content:

```yaml
weekend:
  description: "Weekend long-form reading"
  sources:
    - iq
    - nature
    - guardian
  default_count: 50
```

Use:
```bash
./capcat bundle weekend --count 50 --html
```

## Managing Bundle Sources

### Add Source to Bundle

Edit `sources/active/bundles.yml`:

```yaml
tech:
  sources:
    - ieee
    - mashable
    - gizmodo
    - newsource  # Add here
```

### Remove Source from Bundle

Remove from list:

```yaml
tech:
  sources:
    - ieee
    - mashable
    # gizmodo removed
```

### Move Source Between Bundles

Remove from one, add to another:

```yaml
# Remove from tech
tech:
  sources:
    - ieee
    - mashable

# Add to news
news:
  sources:
    - bbc
    - guardian
    - gizmodo  # Moved here
```

## Bundle Auto-Discovery

Bundles automatically include sources with matching category.

If you have a bundle named "tech":
```yaml
tech:
  sources:
    - ieee  # Explicitly listed
```

And sources with `category: tech`:
- gizmodo (category: tech)
- futurism (category: tech)

These are auto-included without editing bundles.yml.

## Bundle Workflows

### Daily Routine Bundle

Morning, noon, evening collections:

```bash
# Morning (8 AM)
./capcat bundle morning --count 10 --html

# Noon update
./capcat bundle news --count 5

# Evening deep dive
./capcat bundle research --count 20 --media
```

### Weekly Automation

Different bundles each day:

```bash
# Monday - Professional news
./capcat bundle techpro --count 20

# Wednesday - General news
./capcat bundle news --count 25

# Friday - Science
./capcat bundle science --count 30

# Sunday - Everything
./capcat bundle all --count 15
```

## Advanced Bundle Usage

### Override Default Count

Bundles have default counts, but you can override:

```bash
# Use default count
./capcat bundle tech

# Override with custom count
./capcat bundle tech --count 50
```

### Generate HTML Selectively

```bash
# With HTML for browsing
./capcat bundle tech --html

# Without HTML (faster)
./capcat bundle tech
```

### Fetch Multiple Bundles

One after another:

```bash
./capcat bundle tech --count 15
./capcat bundle news --count 10
./capcat bundle science --count 10
```

Or all bundles:

```bash
./capcat bundle --all --count 10
```

## Bundle Best Practices

**Naming:**
- Use lowercase
- Short, descriptive names
- Reflect content type

**Source Selection:**
- Group by topic, not volume
- 2-5 sources per bundle ideal
- More sources = longer fetch time

**Count Settings:**
- Daily: 10-20 articles per source
- Weekly: 30-50 articles per source
- Research: 50+ articles per source

**Organization:**
- Personal bundles for daily routine
- Topical bundles for focused research
- Time-based bundles for schedules

## Troubleshooting

**Bundle not found:**
```bash
# Check bundles.yml exists
ls sources/active/bundles.yml

# List available bundles
./capcat list bundles
```

**Source in bundle fails:**
```bash
# Test individual source
./capcat fetch sourcename --count 3

# Remove failing source from bundle
vim sources/active/bundles.yml
```

**Slow bundle fetch:**
- Reduce count
- Remove slow sources
- Skip --media flag
- Skip --html if not needed

## Next Steps

**Optimize collection:**
- [Customizing Output](06-customizing-output.html) - Control what you collect
- [Automation](07-automation.html) - Schedule bundle fetches

**Technical details:**
- [Configuration Exhaustive](../03-configuration-exhaustive.html) - Bundle configuration reference

## Quick Reference

```bash
# Use bundle
./capcat bundle BUNDLE_NAME

# List bundles
./capcat list bundles

# Override count
./capcat bundle BUNDLE_NAME --count N

# With HTML
./capcat bundle BUNDLE_NAME --html

# All bundles
./capcat bundle --all

# Edit bundles
vim sources/active/bundles.yml
```

## Bundle Configuration File

Location: `sources/active/bundles.yml`

Structure:
```yaml
bundle_name:
  description: "Description of bundle"
  sources:
    - source1
    - source2
    - source3
  default_count: 20
```
