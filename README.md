# Capcat - Archive and Share Articles with Confidence

A dual-mode news archiving tool that captures articles from 17+ sources and converts them into **self-contained, shareable HTML files** with embedded CSS and JavaScript - no external dependencies required.

## Why Capcat?

**Share Articles That Never Break**: Every archived article is a complete, standalone HTML file with all styles and scripts embedded. Send to anyone, open anywhere, years later - it just works.

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
- **Fetch by Source** - Browse 17 news sources (Hacker News, BBC, IEEE, Nature, etc.)
- **Fetch by Bundle** - Curated collections (Tech, AI, Science, News, Sports)
- **Single Article** - Archive any URL instantly
- **Source Management** - Add custom RSS/news sources

### Command Line Mode

```bash
# Fetch curated tech bundle (HN + Lobsters + InfoQ + IEEE)
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

- **17+ News Sources** - HN, BBC, Guardian, Nature, IEEE, Scientific American, and more
- **Intelligent Fallback** - Finds images even when primary extraction misses them
- **Comment Preservation** - Captures discussions with privacy anonymization
- **Media Handling** - Images always downloaded, video/audio/PDFs with `--media` flag

### Bundle System

Pre-configured topic collections:

| Bundle | Sources | Description |
|--------|---------|-------------|
| `tech` | HN, Lobsters, InfoQ | General tech news |
| `techpro` | HN, Lobsters, InfoQ, IEEE, Gizmodo, Futurism | Extended tech coverage |
| `ai` | LessWrong, Google AI, OpenAI, MIT News | AI research and developments |
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

## Output Structure

### Batch Mode (fetch/bundle)
```
../News/news_31-12-2025/
├── Hacker-News_31-12-2025/
│   ├── 01_Article_Title/
│   │   ├── article.md
│   │   ├── html/
│   │   │   └── article.html    # Self-contained HTML with embedded CSS/JS
│   │   ├── images/
│   │   │   ├── content1.jpg
│   │   │   └── content2.png
│   │   └── comments.md
│   └── 02_Another_Article/
└── BBC_31-12-2025/
    └── ...
```

### Single Article Mode
```
../Capcats/cc_31-12-2025-Article-Title/
├── article.md
├── html/
│   └── article.html    # Complete standalone file
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

**Tech**: Hacker News, Lobsters, InfoQ, IEEE Spectrum, Gizmodo, Futurism

**AI**: LessWrong, Google AI Blog, OpenAI Blog, MIT News

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
- Many sources use RSS to bypass anti-bot measures
- Run `./capcat catch` and try individual sources

## Contributing

Contributions welcome! See [CONTRIBUTING.md](https://github.com/stayukasabov/capcat/blob/main/.github/CONTRIBUTING.md)

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Links

- **Website**: [capcat.org](https://capcat.org)
- **Repository**: [github.com/stayukasabov/capcat](https://github.com/stayukasabov/capcat)
- **Issues**: [github.com/stayukasabov/capcat/issues](https://github.com/stayukasabov/capcat/issues)
- **Case Study**: [stayux.substack.com](https://stayux.substack.com)

---

**Archive with confidence. Share without limits.**
