---
layout: default
render_with_liquid: false
---

# Quick Start

Get Capcat running in 5 minutes.

## Install

```bash
pipx install capcat
```

Requires Python 3.9+. `pipx` keeps Capcat isolated from your system Python.

## Verify

```bash
capcat list sources
capcat list bundles
```

## First Fetch

```bash
# Fetch 10 articles from Hacker News
capcat fetch hn --count 10

# Fetch with HTML output
capcat fetch hn --count 10 --html

# Fetch from multiple sources
capcat fetch hn lb --count 5
```

Output is saved to `News/<source>/` in your current directory.

## Single Article

```bash
capcat single https://example.com/some-article
capcat single https://example.com/some-article --html --media
```

Output goes to `Capcats/`.

## Bundles

Bundles are named groups of sources defined in `Config/sources/active/bundles/bundles.yml`.

```bash
capcat list bundles
capcat bundle tech --count 20
capcat bundle --all --count 10
```

## Interactive Mode

```bash
capcat catch
```

Full TUI with source management, bundle runs, and settings.

## Common Flags

| Flag | Effect |
|------|--------|
| `--count N` | Number of articles per source (default: 30) |
| `--html` | Generate browsable HTML alongside Markdown |
| `--media` | Download images and PDFs |
| `--output DIR` | Custom output directory |
| `--update` | Re-fetch existing articles |

## Project Initialisation

On first run in a new directory, Capcat auto-creates `Config/` and output directories. You can also run:

```bash
capcat init
```

## Add a Source

```bash
# Add via RSS/Atom feed URL
capcat add-source --url https://example.com/feed.xml
```

Or drop a YAML file into `Config/sources/active/config_driven/configs/` - see [Source Development](/docs/source-development.html) for the format.
