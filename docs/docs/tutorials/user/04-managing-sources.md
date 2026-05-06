---
layout: default
render_with_liquid: false
---

# Managing Sources

Add, remove, and organise news sources.

## List Active Sources

```bash
capcat list sources
```

## Add a Source

### From RSS/Atom URL

```bash
capcat add-source --url https://example.com/feed.xml
```

Capcat fetches the feed, infers a display name, and creates the YAML config automatically.

### Manual YAML

Drop a file in `Config/sources/active/config_driven/configs/`:

```yaml
display_name: "Example News"
base_url: "https://example.com/"
category: tech
rate_limit: 1.0
article_selectors:
  - ".headline a"
content_selectors:
  - "article .body"
```

See [Source Development](/docs/source-development.html) for the full reference.

### Custom Python Source

For sites needing comment integration or complex scraping - create `Config/sources/active/custom/<name>/source.py`. See [Source Development](/docs/source-development.html).

## Remove a Source

```bash
capcat remove-source          # interactive
capcat remove-source --dry-run  # preview only
capcat remove-source --undo     # undo last removal
```

Only config-driven sources can be removed via CLI. Delete custom source directories manually.

## Test a Source

```bash
capcat fetch <source> --count 5
```

Check `News/<source>/` for output and review any errors in the terminal.

## Verify a Source is Discoverable

```bash
capcat list sources | grep <name>
```

## Organise Into Bundles

Edit `Config/sources/active/bundles/bundles.yml`:

```yaml
bundles:
  tech:
    sources: [hn, lb, ieee, mitnews]
    description: "Tech news"
  science:
    sources: [nature, scientificamerican, mitnews]
    description: "Science news"
```
