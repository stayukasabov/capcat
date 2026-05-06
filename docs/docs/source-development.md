---
layout: default
render_with_liquid: false
---

# Source Development

## Two Source Types

### Config-Driven (no Python required)

Create a YAML file in `Config/sources/active/config_driven/configs/`:

```yaml
display_name: "Example News"
base_url: "https://example.com/"
category: tech
rate_limit: 1.0

article_selectors:
  - ".headline a"
  - "h2.title a"

content_selectors:
  - ".article-body"
  - "article .content"

media:
  download_pdfs: false
  max_pdf_size_mb: 10
```

That's it. Run `capcat list sources` to confirm it's discovered, then `capcat fetch example-news --count 5`.

### Custom Source (Python)

Use when you need comment integration, authentication, or non-standard scraping.

Create `Config/sources/active/custom/<name>/source.py`:

```python
from capcat.core.source_system.base_source import BaseSource

class MySource(BaseSource):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "mysource"
        self.display_name = "My Source"

    def discover_articles(self, count=30):
        # Return list of Article objects
        pass

    def fetch_article_content(self, article):
        # Populate article.content, article.title, etc.
        pass

    def fetch_comments(self, comment_url, article_title, article_folder_path):
        # Optional. Called automatically if article.comment_url is set.
        pass
```

## Rate Limiting

All sources must use `EthicalScrapingManager` for HTTP requests. Never call `session.get()` without rate limiting:

```python
from capcat.core.ethical_scraping import get_ethical_manager

manager = get_ethical_manager()
manager.enforce_rate_limit("example.com", 0.0, min_delay=self.config.rate_limit)
response = self.session.get(url)
```

For sites where robots.txt allows access, use `request_with_backoff()` for automatic 429/503 retry.

## Validate

```bash
capcat fetch mysource --count 5 --html
```

Check the output in `News/mysource/` for content, media, and any errors in the log.

## Config-Driven YAML Reference

| Key | Required | Description |
|-----|----------|-------------|
| `display_name` | yes | Human-readable name shown in TUI |
| `base_url` | yes | Root URL of the site |
| `category` | yes | `tech`, `science`, `news`, etc. |
| `rate_limit` | no | Seconds between requests (default: 1.0) |
| `article_selectors` | yes | CSS selectors for article links |
| `content_selectors` | yes | CSS selectors for article body |
| `media.download_pdfs` | no | Override global PDF setting |
| `media.max_pdf_size_mb` | no | Per-source PDF size cap |

## Testing Your Source

```bash
# Unit tests
cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -q

# Acceptance test against live site
capcat fetch mysource --count 10
```
