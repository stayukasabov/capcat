# Customizing Your Output

Control what Capcat collects and how it's organized.

## What You'll Learn

- Control article counts
- Generate HTML for browser reading
- Download additional media files
- Customize output locations
- Update existing articles

## Article Count Control

### Set Count Per Fetch

```bash
# Fetch 10 articles
./capcat fetch hn --count 10

# Fetch 50 articles
./capcat bundle tech --count 50
```

**Guidelines:**
- Daily routine: 10-20 articles
- Weekly collection: 30-50 articles
- Research deep dive: 50+ articles

### Default Counts

Sources and bundles have defaults (usually 30).

Use defaults:
```bash
./capcat fetch hn  # Uses 30
```

Override:
```bash
./capcat fetch hn --count 15  # Uses 15
```

## HTML Generation

### Why Generate HTML?

Markdown is great for archiving, but HTML is better for reading:
- Browse in web browser
- Click between articles
- Professional styling
- Navigate comments easily

### Generate HTML

Add `--html` flag:

```bash
./capcat fetch hn --count 10 --html
./capcat bundle tech --html
./capcat single URL --html
```

### HTML Output Structure

With `--html` flag:

```
Article_Folder/
├── article.md          # Markdown version
├── html/
│   ├── article.html    # Browsable HTML
│   └── comments.html   # Comments (if available)
└── images/             # Downloaded images
```

Open in browser:
```bash
open Article_Folder/html/article.html
```

## Media Download Control

### Images (Always Downloaded)

Images are always downloaded and embedded:

```bash
./capcat fetch hn --count 10
# Images automatically downloaded
```

### Additional Media (Videos, Audio, PDFs)

Use `--media` flag for additional files:

```bash
./capcat fetch nature --count 10 --media
```

Downloads:
- Videos (MP4, WebM, etc.)
- Audio files (MP3, WAV, etc.)
- Documents (PDF, DOCX, etc.)

**Warning:** `--media` significantly increases:
- Download time
- Disk space usage
- Network bandwidth

### Media Storage

```
Article_Folder/
├── article.md
├── images/      # Always downloaded
└── files/       # Videos, PDFs, audio (with --media)
```

## Output Location

### Default Locations

**Bundle and Fetch (multiple articles):**
```
../News/news_DD-MM-YYYY/Source_DD-MM-YYYY/
```

**Single article:**
```
../Capcats/cc_DD-MM-YYYY-Article-Title/
```

### Custom Output Location

Use `--output` flag:

```bash
# Custom directory
./capcat fetch hn --count 10 --output /path/to/output

# Relative path
./capcat single URL --output ~/Articles

# Current directory
./capcat fetch bbc --output .
```

## Updating Existing Articles

### Update Mode

Re-fetch and overwrite existing articles:

```bash
./capcat fetch hn --count 10 --update
./capcat bundle tech --update
./capcat single URL --update
```

**Use when:**
- Article content was updated
- Want newer comments
- Previous fetch failed/incomplete

**Behavior:**
- Overwrites existing article.md
- Re-downloads media
- Updates timestamps

## Configuration File Customization

### Global Settings

Edit `capcat.yml`:

```bash
vim capcat.yml
```

Common customizations:

```yaml
processing:
  max_workers: 16           # Parallel downloads (faster)
  download_images: true     # Always on
  download_videos: false    # Off unless --media

network:
  connect_timeout: 15       # Connection timeout
  read_timeout: 45          # Read timeout

logging:
  default_level: "INFO"     # Log verbosity
```

Save and settings apply to all future fetches.

### Per-Source Customization

Edit source config:

```bash
vim sources/active/config_driven/configs/sourcename.yaml
```

Customize:
```yaml
timeout: 15.0              # Source-specific timeout
rate_limit: 2.0            # Slower rate limiting
```

## Common Customization Scenarios

### Quick Daily Collection

Fast, no frills:

```bash
./capcat bundle tech --count 15
# No --html (faster)
# No --media (smaller)
# Default output location
```

### Weekend Reading Preparation

Full featured:

```bash
./capcat bundle science --count 40 --html --media
# HTML for browser reading
# Media for offline viewing
# Large count for weekend
```

### Targeted Research

Custom location, specific sources:

```bash
./capcat fetch nature,scientificamerican --count 30 \
  --html --media --output ~/Research/Climate
```

### Archive Update

Refresh existing collection:

```bash
./capcat bundle news --count 20 --update --html
# Updates existing articles
# Regenerates HTML
```

## Logging Control

### File Logging

Save detailed logs:

```bash
./capcat --log-file capcat.log fetch hn --count 10
```

Log includes:
- Detailed processing steps
- Network requests
- Errors and warnings
- Timing information

### Verbosity Levels

**Normal (default):**
```bash
./capcat fetch hn --count 10
```

**Verbose:**
```bash
./capcat --verbose fetch hn --count 10
./capcat -V fetch hn --count 10
```

**Quiet (errors only):**
```bash
./capcat --quiet fetch hn --count 10
./capcat -q fetch hn --count 10
```

## Output Organization Tips

**By Date:**
- Default organization by date
- Easy to find recent articles
- Automatic cleanup by deleting old date folders

**By Source:**
- Each source gets its own folder
- Browse by source preference
- Easy to see source volume

**By Topic:**
- Use custom `--output` for topics
- Create topic directories manually
- Organize by project/research area

## Performance vs Quality

**Fast Collection (no frills):**
```bash
./capcat bundle tech --count 10
# ~1-2 minutes
```

**Balanced:**
```bash
./capcat bundle tech --count 20 --html
# ~3-5 minutes
```

**Full Archive:**
```bash
./capcat bundle tech --count 50 --html --media
# ~10-15 minutes
```

## Environment Variables

Override defaults without editing config:

```bash
# More parallel workers
export CAPCAT_PROCESSING_MAX_WORKERS=16
./capcat bundle tech

# Custom timeout
export CAPCAT_NETWORK_CONNECT_TIMEOUT=20
./capcat fetch bbc --count 30
```

## Next Steps

**Automate your setup:**
- [Automation and Scripting](07-automation.html) - Schedule and script

**Deep customization:**
- [Configuration Exhaustive](../03-configuration-exhaustive.html) - All settings documented

## Quick Reference

```bash
# Article count
--count N

# Generate HTML
--html

# Download all media
--media

# Custom output
--output DIR

# Update existing
--update

# File logging
--log-file FILE

# Verbosity
--verbose / -V
--quiet / -q

# Combined example
./capcat bundle tech --count 20 --html --output ~/News
```
