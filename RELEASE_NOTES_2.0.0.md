# Capcat v2.0.0 Release Notes

**Release Date:** December 31, 2025

Capcat 2.0 is a complete rewrite of the personal news archiving utility, bringing professional-grade features, improved reliability, and an intuitive user experience.

## What's New

### Interactive Mode

Launch the new interactive menu for guided workflows:

```bash
./capcat catch
```

No more memorizing commands. The interactive mode guides you through:
- Selecting sources and bundles
- Configuring media downloads
- Managing sources
- HTML generation

### 12 News Sources

Access curated content from:

**Technology:** Hacker News, Lobsters, InfoQ, IEEE Spectrum, Mashable
**News:** BBC News, The Guardian
**Science:** Nature, Scientific American
**AI:** Google Research, MIT News
**Sports:** BBC Sport

### Bundle System

Fetch topical collections with a single command:

```bash
./capcat bundle tech --count 10
./capcat bundle news --count 15 --media
./capcat bundle science --count 5 --html
```

Available bundles: tech, techpro, news, science, ai, sports

### Professional HTML Output

Generate beautiful, shareable HTML pages with:
- Responsive design
- Professional typography
- Consistent navigation
- Embedded themes

Enable with `--html` flag on any command.

### Intelligent Media Handling

**Always Downloaded:** Images from articles
**Optional (--media flag):** Videos, audio, PDFs, documents

**New Fallback System:** Automatically finds content images when primary extraction misses them.

### Privacy First

- Usernames anonymized as "Anonymous" in comments
- Profile links preserved for attribution
- No personal data stored
- Ethical scraping compliance

## Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/stayukasabov/capcat.git
cd capcat/Application

# Run (automatic setup)
./capcat list sources
```

The wrapper handles:
- Virtual environment creation
- Dependency installation
- Python environment activation

### Manual Setup

```bash
cd capcat/Application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./capcat list sources
```

## Usage Examples

### Fetch Latest Tech News

```bash
# Interactive mode (recommended)
./capcat catch
# Select: Catch articles from a bundle → tech

# Command-line mode
./capcat bundle tech --count 10 --html
```

### Get Specific Sources

```bash
# Fetch from Hacker News and BBC
./capcat fetch hn,bbc --count 15 --media

# Single source
./capcat fetch nature --count 5
```

### Save Single Article

```bash
./capcat single https://news.ycombinator.com/item?id=123456
```

### List Available Options

```bash
# Show all sources
./capcat list sources

# Show bundles
./capcat list bundles
```

## What Changed from v1.x

### Complete Rewrite

v2.0 is not an incremental update. It's a complete architectural rewrite with:

- Plugin-based architecture (easy to add sources)
- Unified article processor (consistent handling)
- Professional HTML generation (shareable output)
- Interactive mode (guided workflows)
- Enhanced error handling (better reliability)

### Breaking Changes

- config command removed (use capcat.yml file)
- Output directory structure changed (date-based organization)
- Command syntax updated (see docs for migration)

## Upgrading from v1.x

**Recommended:** Fresh install

```bash
# Backup your old installation
mv capcat capcat-v1-backup

# Clone v2.0
git clone https://github.com/stayukasabov/capcat.git

# Your old output remains accessible in capcat-v1-backup/News/
```

**Migration Notes:**
- Old capcat.yml config may need updates
- Output structure has changed
- Review new command syntax in docs/quick-start.md

## System Requirements

- Python 3.8 or higher (3.11+ recommended)
- 100MB disk space for dependencies
- Internet connection for article fetching
- macOS, Linux, or Windows

## Documentation

**Quick Start:** docs/quick-start.md
**Interactive Mode:** docs/interactive-mode.md
**Architecture:** docs/architecture.md
**API Reference:** docs/api-reference.md
**Website:** https://stayukasabov.github.io/capcat/

## Known Issues

- Source count in some older documentation may reference 16+ sources (actual: 12)
- config command referenced in older docs (removed in v2.0)

## Support

**Issues:** https://github.com/stayukasabov/capcat/issues
**Documentation:** https://stayukasabov.github.io/capcat/
**Source Code:** https://github.com/stayukasabov/capcat

## Contributors

Built with Claude Code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---

**Full Changelog:** https://github.com/stayukasabov/capcat/blob/main/CHANGELOG.md
