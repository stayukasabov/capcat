---
layout: default
render_with_liquid: false
---

# First 5 Minutes with Capcat

Install and collect your first articles.

## Install

```bash
pipx install capcat
```

Requires Python 3.8+.

## Verify

```bash
capcat list sources
```

You should see 10+ config-driven sources and the custom sources (hn, lb, etc.).

## Your First Fetch

```bash
capcat fetch hn --count 5 --html
```

This fetches 5 articles from Hacker News with HTML output.

## View the Output

```
News/
  hn/
    index.html          ← open this in a browser
    2026-05-06-article-title/
      article.html
      article.md
      comments.html
      comments.md
```

Open `News/hn/index.html` in your browser to browse the fetched articles.

## Next Steps

- [Daily Workflow](./02-daily-workflow.html) - fetch multiple sources efficiently
- [Interactive Mode](./03-interactive-mode.html) - no-typing TUI operation
- [Tutorials Index](/docs/tutorials/)
