# Capcat - Archive and Share Articles with Confidence

A dual-mode news archiving tool that captures articles from 12 curated sources as **clean Markdown files** (Obsidian-ready) with optional **self-contained HTML** output - perfect for knowledge management and offline sharing.

## Why Capcat?

**Build Your Knowledge Base**: Every article saved as clean Markdown - drop directly into Obsidian for full-text search, backlinks, and graph views. Perfect for researchers and lifelong learners.

**Share Without Breaking**: Optional self-contained HTML output with all styles and scripts embedded. Send to anyone, open anywhere, years later - it just works.

**Two Ways to Use**:
- **Interactive Menu** (`./capcat catch`) - Visual interface for browsing sources and bundles
- **Command Line** - Fast automation for power users

**Curated Bundles**: Pre-configured collections like Tech, AI, Science, News - fetch multiple related sources at once.

## Quick Start

### Interactive Mode (Recommended)

```bash
./capcat catch
```

Choose from:
- **Fetch by Source** - Browse 12 curated sources (Hacker News, BBC, IEEE, Nature, etc.)
- **Fetch by Bundle** - Curated collections (Tech, AI, Science, News, Sports)
- **Single Article** - Archive any URL instantly
- **Source Management** - Add custom RSS/news sources

### Command Line Mode

```bash
# Fetch curated tech bundle (IEEE + Mashable)
./capcat bundle tech --count 10

# Fetch specific sources with media
./capcat fetch hn,bbc --count 15 --media

# Archive a single article
./capcat single https://example.com/article

# List all available sources
./capcat list sources
```

## Key Features

### Self-Contained HTML for Easy Sharing

Every article is a **complete, portable HTML file**:
- **Embedded CSS** - All styles inline, no external stylesheets
- **Embedded JavaScript** - Interactive features work offline
- **Local Images** - Downloaded and stored with the article
- **No Dependencies** - Open in any browser, share via email, archive forever

**Perfect for**:
- Email attachments that always look right
- Long-term archiving without link rot
- Offline reading on any device
- Sharing articles that might disappear

### Dual Interface

**Interactive Menu** (`./capcat catch`):
- Visual source selection
- Bundle browsing
- Progress tracking
- Error handling with retries
- No commands to memorize

**Command Line**:
- Fast automation and scripting
- Batch processing
- CI/CD integration
- Power user workflows

### Smart Content Extraction

- **12 Curated Sources** - HN, BBC, Guardian, Nature, IEEE, Scientific American, MIT News, and more
- **Intelligent Fallback** - Finds images even when primary extraction misses them
- **Comment Preservation** - Captures discussions with privacy anonymization
- **Media Handling** - Images always downloaded, video/audio/PDFs with `--media` flag

### Markdown-Native Output

- **Obsidian-Ready** - Clean markdown files you can drop directly into your vault
- **Portable Archives** - Standard markdown format works everywhere
- **Local Images** - All media downloaded and referenced with relative paths
- **Metadata Headers** - Source, date, and URL preserved in frontmatter-style headers

### Bundle System

Pre-configured topic collections:

| Bundle | Sources | Description |
|--------|---------|-------------|
| `tech` | IEEE, Mashable | Consumer technology news |
| `techpro` | HN, Lobsters, InfoQ | Professional developer news |
| `ai` | MIT News, Google Research | AI research and developments |
| `science` | Nature, Scientific American | Scientific publications |
| `news` | BBC, Guardian | General news |
| `sports` | BBC Sport | Sports coverage |

Add your own bundles in `sources/active/bundles.yml`.

## Installation

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/stayukasabov/capcat.git
cd capcat/Application

# Auto-fix dependencies (recommended)
./scripts/fix_dependencies.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### First Run

```bash
# Launch interactive menu
./capcat catch

# Or try a quick fetch
./capcat fetch hn --count 5
```

## Markdown-First Workflow (Obsidian Compatible)

Every article is saved as **clean Markdown** with proper formatting:

```markdown
# Article Title

**Source**: Hacker News | **Date**: 2025-12-31 | **URL**: [Original Link]

## Content

Article body with images referenced locally...

![Image Description](../images/image.jpg)
```

**Perfect for Knowledge Management**:
- **Obsidian**: Drag folders directly into your vault for full-text search and backlinks
- **Notion**: Import markdown files while preserving structure
- **Logseq/Roam**: Compatible with daily notes and graph views
- **Standard Editors**: Works in VS Code, Typora, iA Writer, or any markdown editor

**Metadata Included**:
- Source attribution
- Publication date
- Original URLs
- Local image paths (relative linking)

## Output Structure

### Batch Mode (fetch/bundle)
```
../News/news_31-12-2025/
├── Hacker-News_31-12-2025/
│   ├── 01_Article_Title/
│   │   ├── article.md           # Primary markdown file
│   │   ├── html/
│   │   │   └── article.html     # Self-contained HTML with embedded CSS/JS
│   │   ├── images/
│   │   │   ├── content1.jpg
│   │   │   └── content2.png
│   │   └── comments.md          # Discussions (HN, Reddit sources)
│   └── 02_Another_Article/
└── BBC_31-12-2025/
    └── ...
```

### Single Article Mode
```
../Capcats/cc_31-12-2025-Article-Title/
├── article.md                    # Standalone markdown
├── html/
│   └── article.html              # Complete standalone file
└── images/
    └── ...
```

## Privacy & Ethics

**Privacy-First Design**:
- Usernames anonymized as "Anonymous" in comments
- Profile links preserved for reference
- No personal data collection or storage
- Only public content archived

**Ethical Scraping**:
- Respects robots.txt
- Rate limiting (1 request per 10 seconds)
- Prefers RSS/APIs over HTML scraping
- No paywall circumvention
- Proper source attribution

## Advanced Usage

### Add Custom Sources

```bash
# Interactive source addition
./capcat add-source --url https://example.com/rss

# Or edit configuration
nano sources/active/config_driven/configs/newsource.yaml
```

### Configuration Priority

1. CLI arguments → 2. Environment variables → 3. `capcat.yml` → 4. Defaults

Example `capcat.yml`:
```yaml
output_base_dir: "../MyNews"
max_workers: 8
download_media: true
```

### Automation

```bash
# Daily tech news cron job
0 9 * * * cd /path/to/capcat && ./capcat bundle tech --count 20

# Weekly science digest
0 10 * * 0 cd /path/to/capcat && ./capcat bundle science --count 30 --media
```

## Available Sources

**Tech**: Hacker News, Lobsters, InfoQ, IEEE Spectrum, Mashable

**AI**: Google Research, MIT News

**News**: BBC, The Guardian

**Science**: Nature, Scientific American

**Sports**: BBC Sport

**See all**: `./capcat list sources`

## Documentation

Full documentation at [capcat.org](https://capcat.org):
- [Quick Start Guide](https://capcat.org/docs/quick-start.html)
- [Architecture Overview](https://capcat.org/docs/architecture.html)
- [Source Development](https://capcat.org/docs/source-development.html)
- [Interactive Mode](https://capcat.org/docs/interactive-mode.html)

## Requirements

- Python 3.8+
- Internet connection
- ~50MB disk space for application
- Additional space for archived content

## Troubleshooting

**Dependencies issues?**
```bash
./scripts/fix_dependencies.sh --force
```

**Module not found?**
```bash
./capcat list sources  # Wrapper handles venv activation
```

**Source failing?**
- Check `test-diagnose-*.md` reports
- Most sources use RSS/APIs for reliable, ethical access
- Run `./capcat catch` and try individual sources

## Contributing

Contributions welcome! Open an issue or pull request on [GitHub](https://github.com/stayukasabov/capcat).

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Links

- **Website**: [capcat.org](https://capcat.org)
- **Repository**: [github.com/stayukasabov/capcat](https://github.com/stayukasabov/capcat)
- **Issues**: [github.com/stayukasabov/capcat/issues](https://github.com/stayukasabov/capcat/issues)
- **Case Study**: [stayux.substack.com](https://stayux.substack.com)

---

**Archive with confidence. Share without limits.**
