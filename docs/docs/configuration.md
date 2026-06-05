---
layout: default
render_with_liquid: false
---

# Configuration Guide

## Configuration Hierarchy

Precedence from highest to lowest:

1. CLI flags (`--count`, `--media`, `--html`, `--output`)
2. Environment variables (`CAPCAT_*`)
3. `Config/capcat.yml` - per-vault overrides
4. `Config/Global-settings.yaml` - global defaults
5. Source YAML defaults

## Global Settings

`Config/Global-settings.yaml` (regenerate with `capcat settings --force`):

```yaml
# ─── PDF Downloads ──────────────────────────────────────
pdf:
  max_pdf_size_bytes: 31457280   # 30MB
  max_pdf_per_article: 10

# ─── Media Downloads ─────────────────────────────────────
media:
  download_pdfs: false
  download_images: true
  download_videos: false
  download_audio: false
  download_documents: false

# ─── Network ────────────────────────────────────────────
network:
  connect_timeout: 10
  read_timeout: 30
  media_download_timeout: 60
  head_request_timeout: 10
  max_retries: 3
  retry_delay: 1.0
  crawl_delay: 1.0            # seconds between requests to same domain
  robots_cache_ttl_minutes: 15
  user_agent: "Capcat/2.0 (Personal news archiver)"
  pool_connections: 20
  pool_maxsize: 20

# ─── Processing ─────────────────────────────────────────
processing:
  article_count: 30            # global fallback per source
  max_workers: 8
  conversion_timeout: 30
  max_images: 20
  max_images_media_mode: 1000
  min_image_dimensions: 150    # pixels, skip smaller images
  max_image_size_bytes: 5242880  # 5MB
  max_filename_length: 100
  create_comments_file: true
  remove_style_tags: true
  remove_nav_tags: true
  markdown_line_breaks: true

# ─── UI ─────────────────────────────────────────────────
ui:
  progress_spinner_style: dots  # dots, wave, loading, pulse, bounce, modern

# ─── Logging ────────────────────────────────────────────
logging:
  console_level: INFO          # DEBUG, INFO, WARNING, ERROR
  file_level: DEBUG
  max_log_file_size: 10485760  # 10MB
  log_file_backup_count: 5
  auto_create_log_dir: true
```

## Environment Variables

| Variable | Config key |
|----------|-----------|
| `CAPCAT_POOL_CONNECTIONS` | `network.pool_connections` |
| `CAPCAT_POOL_MAXSIZE` | `network.pool_maxsize` |
| `CAPCAT_PDF_MAX_SIZE` | `pdf.max_pdf_size_bytes` |
| `CAPCAT_PDF_MAX_PER_ARTICLE` | `pdf.max_pdf_per_article` |

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

image_processing:
  max_image_size_mb: 5    # skip images larger than 5MB

media:
  download_pdfs: false
  max_pdf_size_mb: 10
```

`image_processing.max_image_size_mb` overrides the global `processing.max_image_size_bytes` for that source.
`media.download_pdfs` and `media.max_pdf_size_mb` override the global PDF settings for that source.

## Media Flags

`download_files` (images) and `download_pdfs` are independent:

| CLI flag | Effect |
|----------|--------|
| `--media` | Sets both `download_files=True` and `download_pdfs=True` |
| `--pdfs` | Download PDF files only (independent of `--media`) |
| `--no-pdfs` | Explicitly disable PDF downloads for this run |
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
