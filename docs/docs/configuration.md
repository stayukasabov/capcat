---
layout: default
render_with_liquid: false
---

# Configuration Guide

## Configuration Hierarchy

Precedence from highest to lowest:

1. CLI flags (`--count`, `--media`, `--html`, `--output`)
2. Environment variables (`CAPCAT_*`)
3. `Config/capcat.yml` — per-vault overrides
4. `Config/Global-settings.yaml` — global defaults
5. Source YAML defaults

## Global Settings

`Config/Global-settings.yaml`:

```yaml
fetch:
  default_count: 30
  rate_limit: 1.0          # seconds between requests

network:
  pool_connections: 20
  pool_maxsize: 20
  timeout: 30

pdf:
  enabled: false
  max_pdf_size_bytes: 10485760   # 10MB

output:
  html: false
  media: false
```

## Environment Variables

| Variable | Config key |
|----------|-----------|
| `CAPCAT_POOL_CONNECTIONS` | `network.pool_connections` |
| `CAPCAT_POOL_MAXSIZE` | `network.pool_maxsize` |
| `CAPCAT_DEFAULT_COUNT` | `fetch.default_count` |

## Per-Source Config (YAML sources)

Each config-driven source YAML supports:

```yaml
display_name: "Example News"
base_url: "https://example.com/"
category: tech
rate_limit: 1.0

article_selectors:
  - ".headline a"

content_selectors:
  - "article .body"

media:
  download_pdfs: false
  max_pdf_size_mb: 10
```

`media.download_pdfs` and `media.max_pdf_size_mb` override the global PDF settings for that source.

## Media Flags

`download_files` (images) and `download_pdfs` are independent:

| CLI flag | Effect |
|----------|--------|
| `--media` | Sets both `download_files=True` and `download_pdfs=True` |
| `--html` | Generate HTML output only (no media download) |

**TUI PDF prompt:**
- "Yes" → `download_pdfs=True`
- "No" → `download_pdfs=False`
- "Source defaults" → per-source `media.download_pdfs` applies

## Output Directory

Default: current working directory. Override with `--output DIR`.

Structure created automatically:

```
News/<source>/          ← capcat fetch
Capcats/                ← capcat single
.capcat/                ← internal state, do not edit
Config/                 ← user configuration
```

## Initialisation

`capcat init` creates `Config/` with default `Global-settings.yaml` and empty `sources/active/` directories. Run automatically on first use of any command.
