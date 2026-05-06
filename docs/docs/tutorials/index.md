---
layout: default
render_with_liquid: false
---

# Tutorials

Step-by-step guides for common Capcat workflows.

## Getting Started

- [Quick Start](/docs/quick-start.html) — Install and run your first fetch in 5 minutes

## Fetching Articles

### Fetch from a single source

```bash
capcat fetch hn --count 20 --html
```

Output lands in `News/hn/`. Open `News/hn/index.html` in a browser.

### Fetch from multiple sources

```bash
capcat fetch hn lb --count 10 --html
```

### Run a bundle

```bash
capcat list bundles
capcat bundle tech --count 30 --html
```

### Fetch with media

```bash
# Images only
capcat fetch hn --count 10 --html --media

# Single article with everything
capcat single https://example.com/article --html --media
```

## Managing Sources

### Add a source via RSS

```bash
capcat add-source --url https://example.com/feed.xml
```

### Interactive source management

```bash
capcat catch
```

Navigate to "Manage Sources" from the main menu.

### List what's active

```bash
capcat list sources
capcat list bundles
```

## Output Structure

```
News/
  hn/
    index.html                    ← browse all articles
    2026-05-06-article-title/
      article.md
      article.html
      comments.md
      comments.html
      media/
        image1.jpg
Capcats/
  2026-05-06-single-article/
    article.md
    article.html
```

## Building on Capcat

- [Source Development](/docs/source-development.html) — add config-driven or custom sources
- [Architecture](/docs/architecture.html) — understand the pipeline
- [Ethical Scraping](/docs/ethical-scraping.html) — rate limiting and robots.txt compliance
