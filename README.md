# Capcat - A command-line tool designed to solve content preservation challenges with Ethical Scraping.

**v2.0.31** | Python 3.9+ | [capcat.org](https://capcat.org)

Captures articles from 12 built-in sources as clean Markdown files with optional self-contained HTML output. Includes 5 specialized URL processors for platforms like Medium, YouTube, and X. Supports interactive TUI and batch automation.

## Installation

```bash
pipx install capcat
```

Requires Python 3.9+.

## Quick Start

```bash
# Interactive TUI
capcat catch

# Fetch a bundle
capcat bundle tech --count 10

# Fetch specific sources
capcat fetch hn,bbc --count 15

# Archive a single article
capcat single https://example.com/article

# List available sources
capcat list sources

# Show version
capcat --version
```

Capcat initializes the vault automatically on first run.

## Commands

| Command | Description |
|---------|-------------|
| `catch` | Launch the interactive TUI |
| `single <url>` | Archive a single article |
| `fetch <sources>` | Batch fetch from sources (comma-separated) |
| `bundle <name>` | Fetch a pre-configured bundle |
| `list sources` | List all available sources |
| `list bundles` | List all available bundles |
| `add-source --url <url>` | Add a custom RSS/news source |
| `remove-source` | Remove a source |
| `generate-config` | Generate a YAML config |
| `init` | Explicitly scaffold vault (runs automatically on first use) |

## Options

| Flag | Description |
|------|-------------|
| `--count N` | Number of articles to fetch (default: 30) |
| `--output DIR` | Output directory (default: current dir) |
| `--media` | Download images, video, audio, and PDF files |
| `--pdfs` | Download PDF files only (independent of --media) |
| `--html` | Generate self-contained HTML output |
| `--update` | Re-fetch and update existing articles |
| `-V, --verbose` | Verbose output |
| `-q, --quiet` | Quiet output |
| `-L <file>` | Log output to file |
| `--version` | Show version and exit |
| `--help` | Show help and exit |

## Bundles

Pre-configured topic collections:

| Bundle | Sources | Description |
|--------|---------|-------------|
| `tech` | IEEE, Mashable | Consumer technology news |
| `techpro` | HN, Lobsters, InfoQ | Professional developer news |
| `ai` | MIT News, Google Research | AI research and developments |
| `science` | Nature, Scientific American | Scientific publications |
| `news` | BBC, Guardian | General news |
| `sports` | BBC Sport | Sports coverage |

## Available Sources

**Tech Pro**: Hacker News (`hn`), Lobsters (`lb`), InfoQ (`iq`)

**Tech**: IEEE Spectrum (`ieee`), Mashable (`mashable`)

**AI**: Google Research (`google-research`), MIT News (`mitnews`)

**News**: BBC (`bbc`), The Guardian (`guardian`)

**Science**: Nature (`nature`), Scientific American (`scientificamerican`)

**Sports**: BBC Sport (`bbcsport`)

**Custom**: Medium, Substack (add via `capcat add-source`)

## Output Structure

### Batch mode (`fetch` / `bundle`)

```
News/news_DD-MM-YYYY/
├── Hacker-News_DD-MM-YYYY/
│   ├── 01_Article_Title/
│   │   ├── article.md
│   │   ├── comments.md
│   │   ├── html/
│   │   │   ├── article.html
│   │   │   └── comments.html
│   │   └── images/
│   └── 02_Another_Article/
└── BBC_DD-MM-YYYY/
```

### Single article mode

```
Capcats/cc_DD-MM-YYYY-Title/
├── article.md
├── html/
│   └── article.html
└── images/
```

HTML output is fully self-contained - embedded CSS, no external dependencies. Open in any browser, share via email, archive permanently.

## Configuration

Optional `capcat.yml` in your project directory:

```yaml
output_base_dir: "../MyNews"
max_workers: 8
download_media: false
```

Config priority: CLI flag, TUI prompt, per-source `Config/sources/active/<source>/config.yaml`, `Config/Global-settings.yaml`.

## Automation

```bash
# Daily tech news
0 9 * * * cd ~/news && capcat bundle tech --count 20 --html

# Weekly science digest
0 10 * * 0 cd ~/news && capcat bundle science --count 30 --media
```

## Privacy and Ethics

- Usernames anonymized as "Anonymous" in comment archives
- Respects `robots.txt`
- Rate limiting: 1 request per 10 seconds
- Prefers RSS/APIs over HTML scraping
- No paywall circumvention
- Proper source attribution

## Archive Isolation

Every archived file passes through a content sanitizer before saving.
The sanitizer silently removes:

- Tracking pixels and analytics beacons
- Embedded scripts and iframes
- DNS prefetch/preload hints
- Hidden elements with external references
- Known tracker domain resources (Google Analytics, DoubleClick, Facebook Pixel, etc.)

Heuristic detection catches unlisted trackers by identifying:
- 1x1 pixel images
- Query-heavy image URLs (fingerprinting patterns)
- URLs with /collect, /pixel, /beacon, /analytics paths
- Hidden elements containing external references

Article links and source URLs are preserved. The archive is yours to read
offline with zero external connections.

## Documentation

Full documentation at [capcat.org](https://capcat.org):
- [Quick Start Guide](https://capcat.org/docs/quick-start.html)
- [Architecture Overview](https://capcat.org/docs/architecture.html)
- [Source Development](https://capcat.org/docs/source-development.html)
- [Interactive Mode](https://capcat.org/docs/interactive-mode.html)

## Contributing

Open an issue or pull request on [GitHub](https://github.com/stayukasabov/capcat).

## License

MIT License - see [LICENSE.txt](LICENSE.txt)

## Links

- **Website**: [capcat.org](https://capcat.org)
- **Repository**: [github.com/stayukasabov/capcat](https://github.com/stayukasabov/capcat)
- **Issues**: [github.com/stayukasabov/capcat/issues](https://github.com/stayukasabov/capcat/issues)
