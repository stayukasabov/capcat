# Capcat — A command-line tool designed to solve content preservation challenges with Ethical Scraping.

Captures articles from 17+ curated sources as clean Markdown files with optional self-contained HTML output. Supports interactive TUI and batch automation.

## Installation

```bash
pipx install capcat
```

Requires Python 3.8+.

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

No init required — capcat initializes automatically on first run.

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
| `init` | Manually initialize project in current directory |

## Options

| Flag | Description |
|------|-------------|
| `--count N` | Number of articles to fetch (default: 30) |
| `--output DIR` | Output directory (default: current dir) |
| `--media` | Download video, audio, and PDF files |
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

**Tech**: Hacker News (`hn`), Lobsters (`lb`), InfoQ (`iq`), IEEE Spectrum (`ieee`), Mashable, Gizmodo, Futurism

**AI**: Google Research (`googleai`), OpenAI (`openai`), MIT News (`mitnews`), LessWrong (`lesswrong`)

**News**: BBC (`bbc`), The Guardian (`guardian`)

**Science**: Nature (`nature`), Scientific American (`scientificamerican`)

**Sports**: BBC Sport (`bbcsport`)

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

HTML output is fully self-contained — embedded CSS, no external dependencies. Open in any browser, share via email, archive permanently.

## Configuration

Optional `capcat.yml` in your project directory:

```yaml
output_base_dir: "../MyNews"
max_workers: 8
download_media: false
```

Config priority: CLI args → environment variables → `capcat.yml` → defaults.

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

## Documentation

Full documentation at [capcat.org](https://capcat.org):
- [Quick Start Guide](https://capcat.org/docs/quick-start.html)
- [Architecture Overview](https://capcat.org/docs/architecture.html)
- [Source Development](https://capcat.org/docs/source-development.html)
- [Interactive Mode](https://capcat.org/docs/interactive-mode.html)

## Contributing

Open an issue or pull request on [GitHub](https://github.com/stayukasabov/capcat).

## License

MIT License — see [LICENSE.txt](LICENSE.txt)

## Links

- **Website**: [capcat.org](https://capcat.org)
- **Repository**: [github.com/stayukasabov/capcat](https://github.com/stayukasabov/capcat)
- **Issues**: [github.com/stayukasabov/capcat/issues](https://github.com/stayukasabov/capcat/issues)
