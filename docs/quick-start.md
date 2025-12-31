# Quick Start Guide

Get Capcat running in 5 minutes with this streamlined setup guide.

## Prerequisites

- **Python 3.8+** (recommended: 3.11+)
- **Virtual environment** capability
- **Network access** for downloading articles

## Installation

### Automatic Setup (Recommended)

The new wrapper system handles all setup automatically:

```bash
# Navigate to Capcat directory
cd "Capcat/Application"

# Everything is handled automatically - just run capcat!
./capcat list sources
```

**What happens automatically**:
- Detects or creates virtual environment
- Installs dependencies from requirements.txt
- Activates proper Python environment
- Runs capcat command

### Manual Setup (Advanced Users)

If you prefer manual control:

```bash
# Navigate to Capcat directory
cd "Capcat/Application"

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run capcat directly
python capcat.py list sources
```

### Verification

```bash
# Test wrapper system
./capcat list sources

# Should show 25+ sources across 4 categories
# Output: "Tech (4), News (5), Science (3), etc."
```

## Basic Usage

### Interactive Mode (Recommended for New Users)

Launch the interactive menu for guided workflows:

```bash
./capcat catch
```

**Main Menu Options:**
```
  What would you like me to do?

  > Catch articles from a bundle of sources
    Catch articles from a list of sources
    Catch from a single source
    Catch a single article by URL
    Manage Sources (add/remove/configure)
    Exit
```

**Why Use Interactive Mode:**
- No command memorization required
- Guided step-by-step workflows
- Visual source selection
- Built-in source management
- Prevents common errors
- Ideal for daily use

**Quick Examples:**

**Fetch a News Bundle:**
1. `./capcat catch`
2. Select "Catch articles from a bundle"
3. Choose bundle (tech, news, science, etc.)
4. Select HTML generation option
5. Confirm and execute

**Add a New Source:**
1. `./capcat catch`
2. Select "Manage Sources"
3. Select "Add New Source from RSS Feed"
4. Enter RSS feed URL
5. Follow prompts

**Test a Source:**
1. `./capcat catch`
2. Select "Manage Sources"
3. Select "Test a Source"
4. Choose source to test
5. View results

For comprehensive interactive mode documentation, see [Interactive Mode Guide](interactive-mode.html).

### CLI Mode (Advanced Users & Scripts)

#### Single Article Download
```bash
# Download a single article
./capcat single https://example.com/article

# With media files
./capcat single https://bbc.com/news/technology --media
```

#### Batch Downloads
```bash
# Tech news bundle (Hacker News + Lobsters + InfoQ)
./capcat bundle tech --count 10

# General news bundle (BBC + CNN + Reuters)
./capcat bundle news --count 15 --media

# Specific sources
./capcat fetch hn,bbc --count 20
```

#### Discovery Commands
```bash
# List all available sources
./capcat list sources

# List predefined bundles
./capcat list bundles
```

#### File Logging
```bash
# Save detailed logs to file (includes all debug information)
./capcat -L capcat.log bundle tech --count 10

# Verbose console output + file logging
./capcat -V -L debug.log fetch hn --count 15

# Timestamped log files
./capcat -L logs/news-$(date +%Y%m%d-%H%M%S).log bundle news --count 10
```

## Output Structure

```
../News/news_DD-MM-YYYY/           # Batch downloads
├── Hacker-News_DD-MM-YYYY/
│   └── 01_Article_Title/
│       ├── article.md
│       ├── comments.md
│       └── images/
└── BBC-News_DD-MM-YYYY/
    └── 01_Article_Title/
        ├── article.md
        └── images/

../Capcats/                      # Single articles
└── cc_DD-MM-YYYY-Article-Title/
    ├── article.md
    └── images/
```

## Key Features Demo

### 1. Config-Driven Sources (Simple)
```bash
# These sources use YAML configuration (no coding required)
./capcat fetch iq,euronews,straitstimes --count 5
```

### 2. Custom Sources (Complex)
```bash
# These sources have custom Python implementations
./capcat fetch hn,bbc,techcrunch --count 5
```

### 3. Media Handling
```bash
# Images only (default)
./capcat bundle tech --count 5

# All media types (images + videos + documents)
./capcat bundle tech --count 5 --media
```

## Verification

### Test System Health
```bash
# Run comprehensive source test
python test_comprehensive_sources.py

# Quick individual test
./capcat fetch hn --count 3
```

### Expected Results
- **Sources**: 16+ sources discovered
- **Success Rate**: ~90% (14-16/16+ sources working)
- **Performance**: 4-6 seconds average per source
- **Output**: Clean Markdown files with local images

### Source Policy
- **Paywall Exclusion**: Sources with paywalls or subscription requirements are excluded
- **Recently Removed**: Wired, The Verge (moved to paywall model)
- **Bot Protection**: Sources with aggressive anti-bot measures are avoided
- **Use `./capcat list sources`** to see current available sources

### Intelligent Protection System

Capcat includes automatic protection against problematic sites:

**Download Limits (Automatic)**:
- **Normal Articles**: 50 images, 20MB total
- **Suspicious Sites**: 10 images, 5MB total
- **High Risk Sites**: 5 images, 2MB total
- **Link Aggregators**: 0 images, 0MB (blocked)

**Real-World Protection**:
```bash
# Example: consumed.today attempted to download 471 images (103MB)
# Automatically blocked: "LINK_AGGREGATOR detected"
# Protection saved: 103MB of unwanted downloads
```

**Media Flag Behavior**:
```bash
# Without --media flag: Standard protection limits apply
./capcat single https://example.com/article

# With --media flag: Bypass limits for legitimate sites (up to 500MB)
./capcat single https://example.com/article --media

# Note: --media flag ignored for blocked aggregator sites
```

## Wrapper System

Capcat uses a two-layer wrapper system for reliability:

### Architecture
- **`capcat`** - Lightweight 9-line bash script (executable shortcut)
- **`run_capcat.py`** - Comprehensive Python wrapper (handles all logic)
- **`capcat.py`** - Main application code

### Benefits
- **Automatic Environment Management** - No manual venv activation needed
- **Dependency Installation** - Automatically installs requirements.txt
- **Error Handling** - Clear messages for common issues
- **Cross-Platform** - Works on macOS, Linux, Windows

### Entry Points

```bash
# Primary method (recommended)
./capcat command args

# Alternative method (direct Python)
python3 run_capcat.py command args

# Manual method (requires venv activation)
source venv/bin/activate && python capcat.py command args
```

## Common Issues

### 1. Wrapper System Issues
```bash
# If bash wrapper fails, use Python wrapper directly
python3 run_capcat.py list sources

# Check wrapper system health
./capcat --help
```

### 2. Module Not Found
```bash
# Let wrapper handle dependencies automatically
./capcat list sources

# Or manually activate environment (advanced users)
source venv/bin/activate
```

### 3. Virtual Environment Issues
```bash
# Remove and recreate (wrapper will rebuild)
rm -rf venv
./capcat list sources
```

### 4. Network Errors
```bash
# Some sources may have anti-bot protection (normal)
# Success rate of 90% (14-16/25) is expected
```

## Next Steps

- **[Interactive Mode Guide](interactive-mode.html)** - Complete guide to interactive menu system
- **[Source Management Menu](source-management-menu.html)** - Detailed source management operations
- **[Architecture Overview](architecture.html)** - Understand the system design
- **[Source Development](source-development.html)** - Create new sources
- **[Configuration Guide](configuration.html)** - Customize system behavior
- **[Testing Guide](testing.html)** - Run comprehensive tests

## Pro Tips

1. **Use bundles** for related content: `bundle tech`, `bundle news`
2. **Start small** with `--count 5` to test new sources
3. **Monitor performance** - check average processing times
4. **Use --media sparingly** - significantly increases download time
5. **Enable file logging** with `-L logfile.log` for troubleshooting and debugging

---

*You're now ready to use Capcat! For advanced usage, continue to the Architecture Overview.*