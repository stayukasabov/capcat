# CLI Commands Exhaustive Reference

Complete documentation of EVERY command-line interface option, flag, parameter, and workflow in Capcat.

Source: Application/cli.py, Application/capcat.py

## Global Options

These options work with ALL commands.

### --version, -v
```bash
./capcat --version
./capcat -v
```
Displays: `Capcat v2.0.0`

### --verbose, -V
```bash
./capcat --verbose <command>
./capcat -V <command>
```
Enable verbose output logging. Shows:
- Detailed processing information
- Debug-level messages
- Source discovery details
- Network requests
- Article processing steps

**Cannot be used with:** --quiet

### --quiet, -q
```bash
./capcat --quiet <command>
./capcat -q <command>
```
Suppress informational messages. Shows only:
- Warnings
- Errors
- Critical messages

**Cannot be used with:** --verbose

### --config, -C FILE
```bash
./capcat --config custom.yml <command>
./capcat -C ~/.capcat/config.yml <command>
```
Specify custom configuration file path instead of default capcat.yml.

**Default location:** Application/capcat.yml

###

 --log-file, -L FILE
```bash
./capcat --log-file capcat.log <command>
./capcat -L logs/debug-$(date +%Y%m%d).log <command>
```
Write detailed logs to specified file. File logging includes:
- All log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Timestamps for every entry
- Module/function names
- Full stack traces for errors
- Network request/response details

**Log format:** `[YYYY-MM-DD HH:MM:SS] [LEVEL] [module.function:line] Message`

## Commands

### single - Download Single Article

Download and process a single article from any URL.

**Syntax:**
```bash
./capcat single <url> [options]
```

**Required Arguments:**
- `url` - Article URL to download (must be valid HTTP/HTTPS URL)

**Options:**

#### --output, -o DIR
```bash
./capcat single URL --output /path/to/output
./capcat single URL -o ../Capcats
```
Specify output directory for article.

**Default:** Current directory (.)
**Output structure:**
```
<output-dir>/
└── cc_DD-MM-YYYY-Article-Title/
    ├── article.md
    ├── images/
    └── html/ (if --html specified)
```

#### --media, -M
```bash
./capcat single URL --media
./capcat single URL -M
```
Download ALL media types:
- Images (always downloaded, this flag adds others)
- Videos (MP4, WebM, etc.)
- Audio files (MP3, WAV, etc.)
- Documents (PDF, DOCX, etc.)

**Default:** Images only
**Storage:** Files stored in `files/` subdirectory

#### --html, -H
```bash
./capcat single URL --html
./capcat single URL -H
```
Generate HTML version of article in addition to Markdown.

**Output:** Article_Folder/html/article.html
**Features:**
- Professional styling with themes
- Navigation buttons
- Responsive design
- Dark/light mode support

#### --update, -U
```bash
./capcat single URL --update
./capcat single URL -U
```
Update existing article if it already exists.

**Behavior:**
- Overwrites existing article.md
- Re-downloads media files
- Updates timestamps
- Preserves folder structure

**Complete Examples:**
```bash
# Basic single article download
./capcat single https://example.com/article

# Download with all media and HTML
./capcat single https://bbc.com/news/article --media --html

# Update existing article verbosely
./capcat single URL --update --verbose

# Custom output with logging
./capcat single URL --output ~/Articles --log-file fetch.log
```

### fetch - Fetch from Specific Sources

Fetch articles from one or more specific sources.

**Syntax:**
```bash
./capcat fetch <sources> [options]
```

**Required Arguments:**
- `sources` - Comma-separated list of source IDs (no spaces)

**Available Sources:** Use `./capcat list sources` to see all available source IDs.

**Common Source IDs:**
- `hn` - Hacker News
- `lb` - Lobsters
- `iq` - InfoQ
- `bbc` - BBC News
- `guardian` - The Guardian
- `nature` - Nature News
- `ieee` - IEEE Spectrum
- `mitnews` - MIT News
- `bbcsport` - BBC Sport

**Options:**

#### --count, -c N
```bash
./capcat fetch hn --count 10
./capcat fetch hn,bbc -c 50
```
Number of articles to fetch per source.

**Default:** 30
**Range:** 1-1000 (practical limit varies by source)
**Behavior:** Each source fetches N articles independently

#### --output, -o DIR
```bash
./capcat fetch hn --output /path/to/output
./capcat fetch hn -o ../News
```
Specify output directory for articles.

**Default:** Current directory (.)
**Output structure:**
```
<output-dir>/
└── news_DD-MM-YYYY/
    ├── Source1_DD-MM-YYYY/
    │   ├── 01_Article_Title/
    │   ├── 02_Article_Title/
    │   └── ...
    └── Source2_DD-MM-YYYY/
        └── ...
```

#### --media, -M
```bash
./capcat fetch hn,bbc --media
./capcat fetch nature -M
```
Download ALL media types (videos, audio, documents) in addition to images.

**Default:** Images only
**Impact:** Significantly increases download time and disk usage

#### --html, -H
```bash
./capcat fetch hn --html
./capcat fetch hn,bbc -H
```
Generate HTML versions of all articles.

**Output:** Each article gets html/article.html
**Sources with comments:** Also generates html/comments.html

#### --update, -U
```bash
./capcat fetch hn --update
./capcat fetch hn -U
```
Update existing articles if they already exist.

**Complete Examples:**
```bash
# Fetch 10 articles from Hacker News
./capcat fetch hn --count 10

# Fetch from multiple sources
./capcat fetch hn,lb,iq --count 20

# Fetch with all features
./capcat fetch bbc,guardian --count 15 --media --html --verbose

# Fetch to custom location with logging
./capcat fetch nature --count 5 --output ~/Science --log-file science.log
```

### bundle - Fetch from Source Bundles

Fetch articles from predefined source bundles (groups of related sources).

**Syntax:**
```bash
./capcat bundle <bundle-name> [options]
```

**Required Arguments:**
- `bundle-name` - Name of predefined bundle

**Available Bundles:** Use `./capcat list bundles` to see all available bundles.

**Predefined Bundles:**
- `tech` - Technology news (ieee, mashable, gizmodo)
- `techpro` - Advanced tech news (hn, lb, iq)
- `news` - General news (bbc, guardian)
- `science` - Science news (nature, scientificamerican)
- `ai` - AI/ML news (mitnews, googleai, openai)
- `sports` - Sports news (bbcsport)
- `all` - All available sources

**Options:**

#### --count, -c N
```bash
./capcat bundle tech --count 10
./capcat bundle news -c 50
```
Number of articles to fetch per source in bundle.

**Default:** 30
**Behavior:** Each source in bundle fetches N articles

#### --output, -o DIR
```bash
./capcat bundle tech --output /path/to/output
./capcat bundle tech -o ../News
```
Specify output directory.

**Default:** Current directory (.)
**Structure:** Same as `fetch` command

#### --media, -M
```bash
./capcat bundle tech --media
./capcat bundle science -M
```
Download ALL media types for all sources in bundle.

#### --html, -H
```bash
./capcat bundle tech --html
./capcat bundle news -H
```
Generate HTML for all articles from all sources.

#### --all, -A
```bash
./capcat bundle --all
./capcat bundle -A --count 10
```
Fetch from ALL available bundles in order: techpro, tech, news, science, ai.

**Cannot be used with:** bundle-name argument
**Behavior:** Processes bundles sequentially

#### --update, -U
```bash
./capcat bundle tech --update
./capcat bundle tech -U
```
Update existing articles in bundle.

**Complete Examples:**
```bash
# Fetch tech bundle
./capcat bundle tech

# Fetch with custom count
./capcat bundle news --count 20

# Fetch all bundles
./capcat bundle --all --count 10

# Full-featured bundle fetch
./capcat bundle science --count 15 --media --html --verbose

# All bundles with logging
./capcat bundle --all --log-file bundles-$(date +%Y%m%d).log
```

### list - List Sources and Bundles

Display available sources, bundles, or both.

**Syntax:**
```bash
./capcat list [what]
```

**Arguments:**
- `what` - What to list: sources, bundles, or all (default: all)

**Options:** None (this command has no additional options)

**Examples:**

#### List All Sources
```bash
./capcat list sources
```
**Output format:**
```
--- Available Sources ---

TECH:
  - ieee           IEEE Spectrum
  - mashable       Mashable
  - gizmodo        Gizmodo

TECHPRO:
  - hn             Hacker News
  - lb             Lobsters
  - iq             InfoQ

NEWS:
  - bbc            BBC News
  - guardian       The Guardian

SCIENCE:
  - nature         Nature News
  - scientificamerican Scientific American

AI:
  - mitnews        MIT News

SPORTS:
  - bbcsport       BBC Sport

Total: 11 sources
```

#### List All Bundles
```bash
./capcat list bundles
```
**Output format:**
```
--- Available Bundles ---

tech - Technology News
  Sources: ieee, mashable, gizmodo

techpro - Advanced Technology
  Sources: hn, lb, iq

news - General News
  Sources: bbc, guardian

science - Science News
  Sources: nature, scientificamerican

ai - AI & Machine Learning
  Sources: mitnews

sports - Sports News
  Sources: bbcsport

Total: 6 bundles
```

#### List Both
```bash
./capcat list all
./capcat list
```
Displays both sources and bundles sections.

### config - Configuration Management

View or modify Capcat configuration.

**Syntax:**
```bash
./capcat config [options]
```

**Options:**

#### --show, -s
```bash
./capcat config --show
./capcat config -s
```
Display current configuration from capcat.yml.

**Output includes:**
- Network settings (timeouts, user agent)
- Processing settings (workers, media flags)
- Logging configuration
- Output directories
- Source-specific settings

#### --set KEY=VALUE
```bash
./capcat config --set max_workers=16
./capcat config --set download_images=true
```
Set configuration value.

**Cannot be used with:** --show

**Modifiable settings:**
- `max_workers` - Number of parallel workers (1-32)
- `download_images` - Enable/disable image downloads (true/false)
- `download_videos` - Enable/disable video downloads (true/false)
- `connect_timeout` - Network connection timeout (seconds)
- `read_timeout` - Network read timeout (seconds)
- `user_agent` - Custom user agent string

**Note:** Changes are written to capcat.yml immediately.

**Examples:**
```bash
# Show current config
./capcat config --show

# Increase workers
./capcat config --set max_workers=16

# Set custom user agent
./capcat config --set user_agent="MyBot/1.0"
```

### add-source - Add New RSS Source

Interactively add a new RSS-based source.

**Syntax:**
```bash
./capcat add-source --url <rss-feed-url>
```

**Required Options:**
- `--url` - URL of RSS feed to add

**Interactive Workflow:**
1. RSS feed inspection and validation
2. Source ID selection (auto-suggested from feed title)
3. Category selection from existing categories
4. Optional bundle assignment
5. Optional test fetch (recommended)

**What It Creates:**
- YAML config file in: sources/active/config_driven/configs/
- Filename: `<source-id>.yaml`
- Bundle entry (if selected)

**Examples:**
```bash
# Add new RSS source
./capcat add-source --url https://techcrunch.com/feed/

# Interactive flow:
# 1. Inspecting RSS feed...
#    [OK] Feed 'TechCrunch' found.
#
# 2. Configure New Source
#    Source ID: techcrunch
#    Category: tech
#    Add to bundle? Yes
#      Bundle: tech
#    [OK] Added 'techcrunch' to bundle 'tech'.
#
# 3. Running Test Fetch
#    Test fetch? Yes
#    [OK] Source added and verified successfully!
```

**Cancellation:** Press Ctrl+C at any prompt to cancel operation.

### remove-source - Remove Existing Sources

Interactively remove one or more sources with safety features.

**Syntax:**
```bash
./capcat remove-source [options]
```

**Interactive Mode (No Options):**
```bash
./capcat remove-source
```
Launches interactive removal with checkbox selection:
1. Displays all available sources
2. Select sources with spacebar
3. Review changes
4. Confirm removal
5. Automatic backup created
6. Sources removed

**Options:**

#### --dry-run, -n
```bash
./capcat remove-source --dry-run
./capcat remove-source -n
```
Preview changes without actually removing anything.

**Output shows:**
- Which files would be removed
- Which bundle entries would be deleted
- Backup that would be created
- No actual changes made

#### --batch, -b FILE
```bash
./capcat remove-source --batch sources.txt
./capcat remove-source -b remove-list.txt
```
Remove sources listed in file (one source ID per line).

**File format:**
```
techcrunch
oldnewssite
discontinued-source
```

**Behavior:**
- Reads file line by line
- Validates all source IDs first
- Confirms before removal (unless --force)
- Creates backup

#### --undo, -u [BACKUP_ID]
```bash
./capcat remove-source --undo
./capcat remove-source --undo latest
./capcat remove-source --undo backup_20251025_143022
```
Restore sources from backup.

**Arguments:**
- No argument or `latest` - Restore most recent backup
- `BACKUP_ID` - Restore specific backup by ID

**Backup ID format:** `backup_YYYYMMDD_HHMMSS`

**Restores:**
- All config files
- Bundle definitions
- Registry cache

#### --no-backup
```bash
./capcat remove-source --no-backup
./capcat remove-source --no-backup --force
```
Skip creating backup before removal.

**Warning:** No undo capability without backup. Use with extreme caution.

#### --no-analytics
```bash
./capcat remove-source --no-analytics
```
Skip displaying usage analytics for sources.

**Default behavior:** Shows usage statistics before removal

#### --force, -f
```bash
./capcat remove-source --force
./capcat remove-source -f --batch sources.txt
```
Skip all confirmation prompts.

**Use cases:**
- Automated scripts
- CI/CD pipelines
- Batch operations

**Warning:** No confirmation, immediate removal.

**Complete Examples:**
```bash
# Interactive removal
./capcat remove-source

# Preview without removing
./capcat remove-source --dry-run

# Batch removal
./capcat remove-source --batch old-sources.txt

# Forced batch removal without backup
./capcat remove-source --force --no-backup --batch remove.txt

# Restore last removal
./capcat remove-source --undo

# Restore specific backup
./capcat remove-source --undo backup_20251025_120000
```

**Backup Locations:**
```
Application/
└── .capcat-backups/
    ├── backup_20251025_143022/
    │   ├── configs/
    │   ├── bundles.yml
    │   └── manifest.json
    └── backup_20251025_150033/
        └── ...
```

### generate-config - Generate Source Config

Launch interactive wizard to create comprehensive YAML source configuration.

**Syntax:**
```bash
./capcat generate-config [options]
```

**Interactive Wizard Steps:**
1. Source ID and display name
2. Category selection
3. Base URL
4. Discovery method (RSS or HTML)
5. Article link selectors (CSS/XPath)
6. Content extraction selectors
7. Image processing configuration
8. Author/date extraction patterns
9. Rate limiting settings
10. Request timeout
11. Skip patterns
12. Template selection

**Options:**

#### --output, -o FILE
```bash
./capcat generate-config --output custom.yaml
./capcat generate-config -o /path/to/config.yaml
```
Specify output file path.

**Default:** sources/active/config_driven/configs/<source-id>.yaml

**Output Format:**
```yaml
# Generated configuration
display_name: "Example Source"
base_url: "https://example.com/"
category: "tech"
timeout: 10.0
rate_limit: 1.0

rss_config:
  feed_url: "https://example.com/feed.xml"
  use_rss_content: true

article_selectors:
  - ".headline a"
  - ".article-title a"

content_selectors:
  - ".article-content"
  - ".post-body"

image_processing:
  selectors:
    - "img"
    - ".content img"
  url_patterns:
    - "example.com/"
  skip_selectors:
    - ".sidebar img"

skip_patterns:
  - "/about"
  - "/contact"
  - "?utm_"
```

**Examples:**
```bash
# Interactive generation
./capcat generate-config

# Save to custom location
./capcat generate-config --output ~/configs/newsource.yaml
```

**Next Steps After Generation:**
```bash
# Review generated config
cat sources/active/config_driven/configs/newsource.yaml

# Test source
./capcat fetch newsource --count 5

# Add to bundle (manual edit)
vim sources/active/bundles.yml
```

### catch - Interactive Mode

Launch interactive menu interface for all Capcat operations.

**Syntax:**
```bash
./capcat catch
```

**No options:** This command has no additional flags or options.

**Main Menu Options:**
1. Catch articles from a bundle of sources
2. Catch articles from a list of sources
3. Catch from a single source
4. Catch a single article by URL
5. Manage Sources (add/remove/configure)
6. Exit

**Navigation:**
- Arrow keys: Move between options
- Enter: Select option
- Ctrl+C: Cancel/go back

**Sub-menu: Manage Sources**
1. Add New Source from RSS Feed
2. Generate Custom Source Config
3. Remove Existing Sources
4. List All Sources
5. Test a Source
6. Back to Main Menu

**Terminal Output:**
```
      ____
    / ____|                     _
   | |     __ _ _ __   ___ __ _| |_
   | |    / _  |  _ \ / __/ _  | __|
   | |___| (_| | |_) | (_| (_| | |_
    \_____\__,_|  __/ \___\__,_|\__|
               | |
               |_|

  What would you like me to do?

  > Catch articles from a bundle of sources
    Catch articles from a list of sources
    Catch from a single source
    Catch a single article by URL
    Manage Sources (add/remove/configure)
    Exit

   (Use arrow keys to navigate)
```

**Example Session:**
```bash
$ ./capcat catch

# User selects: "Catch articles from a bundle of sources"
# System shows bundle list, user selects "tech"
# System asks: "Generate HTML for web browsing?"
# User selects: "Yes"

--------------------
SUMMARY
Action: bundle
Bundle: tech
Generate HTML: true
--------------------

Executing command...
[Article processing begins]
```

**See:** docs/tutorials/02-interactive-mode-exhaustive.md for complete interactive mode documentation.

## Command Combinations

### Typical Workflows

#### Daily News Collection
```bash
# Morning routine: fetch all news
./capcat bundle news --count 20 --html

# Evening: fetch tech updates
./capcat bundle tech --count 10
```

#### Research Workflow
```bash
# Collect science articles with all media
./capcat bundle science --count 30 --media --log-file research.log

# Add specific article found during research
./capcat single https://nature.com/article/12345 --media --html
```

#### Source Management Workflow
```bash
# List current sources
./capcat list sources

# Add new source
./capcat add-source --url https://newssite.com/feed.xml

# Test new source
./capcat fetch newsource --count 3

# Remove old sources
./capcat remove-source --batch old-sources.txt
```

#### Automated Collection Script
```bash
#!/bin/bash
# Daily collection script

LOG_FILE="logs/daily-$(date +%Y%m%d).log"

# Collect from all bundles
./capcat bundle --all --count 20 --html --log-file "$LOG_FILE"

# Check if successful
if [ $? -eq 0 ]; then
    echo "Collection successful" >> "$LOG_FILE"
else
    echo "Collection failed" >> "$LOG_FILE"
    exit 1
fi
```

## Exit Codes

All commands return standard exit codes:

- `0` - Success (all operations completed)
- `1` - General error (command failed)
- `2` - Invalid arguments (validation failed)
- `130` - User interrupt (Ctrl+C pressed)

**Usage in scripts:**
```bash
./capcat fetch hn --count 10
if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed"
    exit 1
fi
```

## Environment Variables

Capcat respects these environment variables:

### CAPCAT_OUTPUT_DIR
```bash
export CAPCAT_OUTPUT_DIR="/custom/path"
./capcat fetch hn
```
Override default output directory for all commands.

### CAPCAT_DEFAULT_COUNT
```bash
export CAPCAT_DEFAULT_COUNT=50
./capcat fetch hn  # Uses 50 instead of 30
```
Override default article count.

### CAPCAT_CONFIG
```bash
export CAPCAT_CONFIG="~/.capcat/custom.yml"
./capcat fetch hn
```
Override default configuration file location.

### CAPCAT_LOG_LEVEL
```bash
export CAPCAT_LOG_LEVEL=DEBUG
./capcat fetch hn
```
Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL

### CAPCAT_MAX_WORKERS
```bash
export CAPCAT_MAX_WORKERS=16
./capcat bundle all
```
Override parallel worker count.

## Configuration Priority

Settings are applied in this order (highest to lowest priority):

1. Command-line arguments (`--count 10`)
2. Environment variables (`CAPCAT_DEFAULT_COUNT=10`)
3. Configuration file (`capcat.yml: default_count: 10`)
4. Default values (hard-coded: 30)

**Example:**
```bash
# capcat.yml has: default_count: 20
# Environment: CAPCAT_DEFAULT_COUNT=40
# Command: --count 10

./capcat fetch hn  # Uses 10 (CLI wins)
```

## Error Handling

### Network Errors
```bash
$ ./capcat fetch hn
Error: Failed to connect to news.ycombinator.com
Network timeout after 10 seconds
```

### Invalid Source
```bash
$ ./capcat fetch nonexistent
Error: Unknown sources: nonexistent
Available: hn, lb, iq, bbc, guardian, ...
```

### Invalid URL
```bash
$ ./capcat single not-a-url
Error: Invalid URL format: not-a-url
Must start with http:// or https://
```

### Permission Denied
```bash
$ ./capcat fetch hn --output /root/articles
Error: Permission denied: /root/articles
Cannot create output directory
```

### Disk Space
```bash
$ ./capcat bundle all --media
Warning: Low disk space (< 1GB available)
Consider using --no-media flag
```

## Debugging Commands

### Verbose Output
```bash
# Maximum verbosity with file logging
./capcat -V --log-file debug.log fetch hn --count 3
```

### Dry Run (Remove Command)
```bash
# Preview what would be removed
./capcat remove-source --dry-run
```

### Test Single Article
```bash
# Test article processing
./capcat single URL --verbose
```

### List and Verify Sources
```bash
# Check source availability
./capcat list sources
```

### Configuration Validation
```bash
# Show current config
./capcat config --show
```

## Source Code Locations

All CLI functionality implemented in:
- Application/cli.py - Argument parsing, subcommands
- Application/capcat.py - Main application logic
- Application/core/ - Core processing modules

Function reference:
- `create_parser()` - Application/cli.py:501 - Parser creation
- `parse_arguments()` - Application/cli.py - Argument parsing
- `validate_arguments()` - Application/cli.py:756 - Validation
- `process_sources()` - Application/capcat.py:55 - Source processing
- `add_source()` - Application/cli.py:200 - Add source command
- `remove_source()` - Application/cli.py:339 - Remove source command
- `generate_config_command()` - Application/cli.py:457 - Config generation

## Related Documentation

- Interactive Mode: docs/tutorials/02-interactive-mode-exhaustive.md
- Configuration: docs/tutorials/03-configuration-exhaustive.md
- Source System: docs/tutorials/04-source-system-exhaustive.md
- API Reference: docs/api-reference.md
