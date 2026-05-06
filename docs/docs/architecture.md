---
layout: default
render_with_liquid: false
---

# Architecture Overview

## System Design

Capcat uses a hybrid architecture: config-driven sources for straightforward RSS/HTML scraping, and custom Python sources for sites requiring comment integration or complex scraping logic.

## Source System

### Config-Driven Sources (10 active)

YAML-based configurations requiring no Python. Add a file to `Config/sources/active/config_driven/configs/` and the source is live.

Active: BBC News, BBC Sport, Google Research, The Guardian, IEEE Spectrum, InfoQ, Mashable, MIT News, Nature, Scientific American.

### Custom Sources (7 active)

Python implementations in `Config/sources/active/custom/`. Used where comment threads, authentication, or non-standard scraping is needed.

Active: Hacker News, Lobsters, Medium, Substack, Twitter/X, Vimeo, YouTube.

## Processing Pipeline

```
capcat fetch <source>
       |
       v
SourceRegistry  →  SourceFactory  →  Source instance
                                            |
                              article discovery (RSS / scrape)
                                            |
                              UnifiedSourceProcessor (8 workers)
                                            |
                              ArticleFetcher  +  fetch_comments()
                                            |
                              MediaProcessor  →  images / PDFs
                                            |
                              HTMLGenerator   →  article HTML
                                            |
                              News/<source>/  (output directory)
```

## Key Components

### SourceRegistry
Auto-discovers all sources from `Config/sources/active/`. Singleton - call `get_source_registry()`.

### UnifiedSourceProcessor
`ThreadPoolExecutor(max_workers=8)` processes articles concurrently. Calls `ArticleFetcher` and `fetch_comments()` per article.

### EthicalScrapingManager
- Robots.txt caching (15-minute TTL)
- `enforce_rate_limit()` - thread-safe slot reservation, used by all sources
- `request_hn_api()` - HN-specific Firebase API wrapper with backoff
- `request_with_backoff()` - exponential backoff for 429/503 errors

### SessionPool
`pool_connections=20, pool_maxsize=20` - shared across all workers via `get_session_pool()`.

### HTMLGenerator
Six templates: `article-with-comments.html`, `article-no-comments.html`, `comments-with-navigation.html`, `article-capcats.html`, `root-index.html`, `source-index.html`.

## Directory Layout

```
~/.capcat/              ← internal state (do not edit)
Config/
  sources/active/
    config_driven/configs/   ← YAML source configs
    custom/<name>/source.py  ← Python source implementations
    bundles/bundles.yml
  themes/               ← CSS overrides
News/                   ← batch fetch output
Capcats/                ← single-article output
```

## Configuration Hierarchy

1. CLI flags (highest priority)
2. Environment variables (`CAPCAT_*`)
3. `Config/Global-settings.yaml`
4. `Config/capcat.yml` (per-vault overrides)
5. Source YAML defaults (lowest priority)

## Design Principles

- No code required to add a config-driven source
- Rate limiting is always on - never bypassable per-source
- Privacy by default: usernames replaced with "Anonymous" in comment output
- `download_files` (images) and `download_pdfs` are independent flags; `--media` sets both
